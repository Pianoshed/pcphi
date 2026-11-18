from datetime import datetime
from xml.sax.saxutils import escape
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, send_from_directory, current_app, Response
from sqlalchemy.exc import IntegrityError
from .. import content as c
from ..extensions import db, limited
from ..forms import SubscribeForm, ContactForm, EnquiryForm
from ..mail import send_mail
from ..models import Programme, Article, Subscriber, ContactMessage, utcnow
from ..util import like

bp = Blueprint("public", __name__)
page = lambda: request.args.get("page", 1, type=int)

@bp.get("/")
def home():
    progs = Programme.query.filter_by(published=True).order_by(Programme.created_at.desc()).limit(3).all()
    news = Article.query.filter_by(published=True).order_by(Article.created_at.desc()).limit(3).all()
    return render_template("home.html", progs=progs, news=news, form=SubscribeForm())

@bp.get("/about")
def about(): return render_template("about.html")

@bp.get("/goals")
def goals(): return render_template("goals.html")

@bp.get("/thematic-areas")
def themes(): return render_template("thematic_areas.html")

@bp.get("/governance")
def governance(): return render_template("governance.html")

@bp.get("/programmes")
def programmes():
    q, area, status, s = Programme.query.filter_by(published=True), request.args.get("area", ""), request.args.get("status", ""), request.args.get("q", "").strip()[:80]
    if area in [t[0] for t in c.THEMES]: q = q.filter_by(thematic_area=area)
    if status in c.STATUSES: q = q.filter_by(status=status)
    if s: q = q.filter(Programme.title.ilike(like(s), escape="\\") | Programme.description.ilike(like(s), escape="\\"))
    args = {k: v for k, v in (("area", area), ("status", status), ("q", s)) if v}
    return render_template("programmes.html", p=q.order_by(Programme.created_at.desc()).paginate(page=page(), per_page=9, error_out=False), args=args, area=area, status=status, s=s)

@bp.get("/programmes/<slug>")
def programme_detail(slug):
    p = Programme.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template("programme_detail.html", p=p, related=[a for a in p.articles if a.published])

@bp.get("/resources")
def resources():
    q, cat, s = Article.query.filter_by(published=True), request.args.get("category", ""), request.args.get("q", "").strip()[:80]
    if cat in c.CATEGORIES: q = q.filter_by(category=cat)
    if s: q = q.filter(Article.title.ilike(like(s), escape="\\") | Article.excerpt.ilike(like(s), escape="\\") | Article.content.ilike(like(s), escape="\\"))
    args = {k: v for k, v in (("category", cat), ("q", s)) if v}
    return render_template("resources.html", p=q.order_by(Article.created_at.desc()).paginate(page=page(), per_page=9, error_out=False), args=args, cat=cat, s=s)

@bp.get("/resources/<slug>")
def article_detail(slug):
    return render_template("article_detail.html", a=Article.query.filter_by(slug=slug, published=True).first_or_404())

def _store_message(form, subject):
    db.session.add(ContactMessage(name=form.name.data.strip(), email=form.email.data.strip().lower(), subject=subject, message=form.message.data.strip()))
    db.session.commit()

@bp.route("/get-involved", methods=["GET", "POST"])
@bp.route("/get-involved/<key>", methods=["POST"])
@limited(6, 3600, "enquiry")
def get_involved(key=None):
    if key and key not in c.PATHWAYS: abort(404)
    forms = {k: EnquiryForm(formdata=request.form if k == key else None) for k in c.PATHWAYS}
    if key and forms[key].validate_on_submit():
        if not forms[key].website.data: _store_message(forms[key], "Get involved: " + c.PATHWAYS[key][0])
        flash("Thank you. Your enquiry has been received and PCPHI will respond by email.", "success")
        return redirect(url_for(".get_involved"))
    return render_template("get_involved.html", forms=forms, active=key)

@bp.route("/subscribe", methods=["GET", "POST"])
@limited(8, 3600, "subscribe")
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():
        if form.website.data: return redirect(url_for(".subscribe_done"))  # honeypot: silently ignore bots
        email, name, interests = form.email.data.strip().lower(), (form.full_name.data or "").strip() or None, ", ".join(form.interests.data or [])
        sub = Subscriber.query.filter_by(email=email).first()
        if sub and sub.is_active:
            form.email.errors.append("This email address is already subscribed.")
        else:
            sub = sub or Subscriber(email=email)
            sub.full_name, sub.interests, sub.consent, sub.is_active, sub.subscribed_at, sub.unsubscribed_at = name, interests, True, True, utcnow(), None
            db.session.add(sub)
            try: db.session.commit()
            except IntegrityError: db.session.rollback(); form.email.errors.append("This email address is already subscribed.")
            else:
                link = url_for(".unsubscribe", token=sub.token(), _external=True)
                mailed = send_mail(email, "Welcome to PCPHI updates", f"Thank you for subscribing to updates from {c.ORG["name"]}.\n\nTo unsubscribe at any time: {link}\n")
                session["subscribed"] = {"mailed": mailed}
                return redirect(url_for(".subscribe_done"))
    elif request.method == "POST": flash("Please check the highlighted fields and try again.", "error")
    return render_template("subscribe.html", form=form)

@bp.get("/subscribe/done")
def subscribe_done():
    state = session.pop("subscribed", None)
    return render_template("subscribe.html", form=None, done=state) if state else redirect(url_for(".subscribe"))

@bp.route("/unsubscribe/<token>", methods=["GET", "POST"])
def unsubscribe(token):
    sub = Subscriber.from_token(token) or abort(404)
    if request.method == "POST":
        sub.is_active, sub.unsubscribed_at = False, utcnow(); db.session.commit()
    return render_template("unsubscribe.html", sub=sub)

@bp.route("/contact", methods=["GET", "POST"])
@limited(6, 3600, "contact")
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        if not form.website.data: _store_message(form, form.subject.data.strip())
        flash("Thank you. Your message has been received.", "success")
        return redirect(url_for(".contact"))
    return render_template("contact.html", form=form)

@bp.get("/media/<path:name>")
def media(name):
    r = send_from_directory(current_app.config["UPLOAD_DIR"], name, max_age=604800)
    r.headers["Content-Security-Policy"] = "default-src 'none'"
    return r

@bp.get("/sitemap.xml")
def sitemap():
    base = current_app.config["SITE_URL"] or request.url_root.rstrip("/")
    top = {"public.home": ("1.0", "weekly"), "public.about": ("0.8", "monthly"), "public.programmes": ("0.9", "weekly"), "public.resources": ("0.8", "weekly")}
    pages = [(url_for(e), None, *top.get(e, ("0.6", "monthly"))) for e in ("public.home", "public.about", "public.goals", "public.themes", "public.governance", "public.programmes", "public.resources", "public.get_involved", "public.subscribe", "public.contact")]
    pages += [(url_for(".programme_detail", slug=p.slug), p.updated_at, "0.7", "monthly") for p in Programme.query.filter_by(published=True)]
    pages += [(url_for(".article_detail", slug=a.slug), a.updated_at, "0.7", "monthly") for a in Article.query.filter_by(published=True)]
    xml = "".join(f"<url><loc>{escape(base + u)}</loc>{f'<lastmod>{d:%Y-%m-%d}</lastmod>' if d else ''}<changefreq>{cf}</changefreq><priority>{pr}</priority></url>" for u, d, pr, cf in pages)
    return Response(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{xml}</urlset>', mimetype="application/xml", headers={"Cache-Control": "public, max-age=3600"})

@bp.get("/robots.txt")
def robots():
    base = current_app.config["SITE_URL"] or request.url_root.rstrip("/")
    return Response(f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /unsubscribe/\nSitemap: {base}/sitemap.xml\n", mimetype="text/plain")

@bp.get("/llms.txt")
def llms():
    base = current_app.config["SITE_URL"] or request.url_root.rstrip("/")
    lines = [f"# {c.ORG['name']}", "", f"> {c.ORG['name']} ({c.ORG['short']}), Ondo State, Nigeria.", "", "## Key pages", ""]
    lines += [f"- [{t}]({base}{url_for(e)})" for t, e in (("About", "public.about"), ("Goals", "public.goals"), ("Thematic areas", "public.themes"), ("Governance", "public.governance"), ("Programmes", "public.programmes"), ("Resources", "public.resources"), ("Get involved", "public.get_involved"), ("Contact", "public.contact"))]
    lines += ["", f"Sitemap: {base}/sitemap.xml", ""]
    return Response("\n".join(lines), mimetype="text/plain")