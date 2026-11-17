import csv, io
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, Response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db, hits, login_manager
from ..forms import LoginForm, ProgrammeForm, ArticleForm
from ..models import AdminUser, Programme, Article, Subscriber, ContactMessage
from ..util import unique_slug, save_image, delete_image, safe_next

bp = Blueprint("admin", __name__)
_DUMMY = generate_password_hash("not-a-real-password")  # equalises timing for unknown usernames
KINDS = {"programmes": (Programme, ProgrammeForm, "image"), "articles": (Article, ArticleForm, "featured_image")}

@bp.before_request
def guard():  # every admin route requires login unless explicitly the login page
    if request.endpoint != "admin.login" and not current_user.is_authenticated:
        return login_manager.unauthorized()

def admin_only(f):
    @wraps(f)
    def inner(*a, **kw):
        if current_user.role != "admin": abort(403)
        return f(*a, **kw)
    return inner

def listing(title, headers, rows, **kw): return render_template("admin/list.html", title=title, headers=headers, rows=rows, **kw)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated: return redirect(url_for(".dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        name = form.username.data.strip().lower(); keys = (f"login-ip:{request.remote_addr}", f"login-user:{name}")
        if any(hits.count(k, 900) >= 5 for k in keys): abort(429)
        u = AdminUser.query.filter(db.func.lower(AdminUser.username) == name).first()
        good = check_password_hash(u.password_hash if u else _DUMMY, form.password.data)
        if u and good and u.is_active:
            session.clear(); login_user(u); session.permanent = True
            return redirect(safe_next(request.args.get("next")) or url_for(".dashboard"))
        for k in keys: hits.add(k)
        flash("Invalid username or password.", "error")
    return render_template("admin/login.html", form=form)

@bp.post("/logout")
def logout():
    logout_user(); session.clear(); flash("You have been signed out.", "success")
    return redirect(url_for(".login"))

@bp.get("/")
def dashboard():
    stats = [("Programmes", Programme.query.count()), ("Published programmes", Programme.query.filter_by(published=True).count()),
             ("Articles", Article.query.count()), ("Published articles", Article.query.filter_by(published=True).count())]
    if current_user.role == "admin":
        stats += [("New messages", ContactMessage.query.filter_by(status="new").count()), ("Active subscribers", Subscriber.query.filter_by(is_active=True).count())]
    return render_template("admin/dashboard.html", stats=stats)

@bp.get("/<any(programmes,articles):kind>")
def items(kind):
    Model = KINDS[kind][0]; admin = current_user.role == "admin"; rows = []
    for o in Model.query.order_by(Model.updated_at.desc()):
        pub = url_for("public." + ("programme_detail" if kind == "programmes" else "article_detail"), slug=o.slug)
        acts = [("Edit", url_for(".item_edit", kind=kind, id=o.id), "get", "", ""),
                ("Unpublish" if o.published else "Publish", url_for(".item_toggle", kind=kind, id=o.id), "post", "", "btn-solid")]
        if o.published: acts.append(("View", pub, "get", "", ""))
        if admin: acts.append(("Delete", url_for(".item_delete", kind=kind, id=o.id), "post", "Delete this permanently?", "btn-danger"))
        rows.append({"cells": [o.title, getattr(o, "status", None) or o.category, "Published" if o.published else "Draft", o.updated_at.strftime("%d %b %Y")], "actions": acts})
    return listing(kind.title(), ["Title", "Status / category", "Visibility", "Updated"], rows, new=url_for(".item_edit", kind=kind))

@bp.route("/<any(programmes,articles):kind>/new", methods=["GET", "POST"])
@bp.route("/<any(programmes,articles):kind>/<int:id>/edit", methods=["GET", "POST"])
def item_edit(kind, id=None):
    Model, Form, imgf = KINDS[kind]; obj = db.get_or_404(Model, id) if id else Model()
    form = Form(obj=obj)
    if kind == "articles":
        form.programme_id.choices = [(0, "None")] + [(p.id, p.title) for p in Programme.query.order_by(Programme.title)]
        if request.method == "GET": form.programme_id.data = obj.programme_id or 0
    if form.validate_on_submit():
        try: new_img = save_image(getattr(form, imgf).data)
        except ValueError as e: getattr(form, imgf).errors = [str(e)]
        else:
            for f in form:
                if f.name not in (imgf, "csrf_token"): setattr(obj, f.name, f.data)
            if kind == "articles": obj.programme_id = obj.programme_id or None
            else: obj.location = (obj.location or "").strip() or None
            if not obj.slug: obj.slug = unique_slug(Model, obj.title)
            if new_img: delete_image(getattr(obj, imgf)); setattr(obj, imgf, new_img)
            db.session.add(obj); db.session.commit(); flash("Saved.", "success")
            return redirect(url_for(".items", kind=kind))
    return render_template("admin/edit.html", form=form, title=("Edit " if id else "New ") + kind[:-1], back=url_for(".items", kind=kind))

@bp.post("/<any(programmes,articles):kind>/<int:id>/toggle")
def item_toggle(kind, id):
    o = db.get_or_404(KINDS[kind][0], id); o.published = not o.published; db.session.commit()
    flash("Published." if o.published else "Unpublished.", "success"); return redirect(url_for(".items", kind=kind))

@bp.post("/<any(programmes,articles):kind>/<int:id>/delete")
@admin_only
def item_delete(kind, id):
    Model, _, imgf = KINDS[kind]; o = db.get_or_404(Model, id); delete_image(getattr(o, imgf)); db.session.delete(o); db.session.commit()
    flash("Deleted.", "success"); return redirect(url_for(".items", kind=kind))

@bp.get("/messages")
@admin_only
def messages():
    rows = [{"cells": [m.created_at.strftime("%d %b %Y %H:%M"), m.name, m.email, m.subject, m.status], "more": m.message, "actions":
             [(s.title(), url_for(".message_status", id=m.id, status=s), "post", "", "") for s in ("read", "archived") if s != m.status]
             + [("Delete", url_for(".message_delete", id=m.id), "post", "Delete this message permanently?", "btn-danger")]}
            for m in ContactMessage.query.order_by(ContactMessage.created_at.desc())]
    return listing("Messages", ["Received", "Name", "Email", "Subject", "Status"], rows)

@bp.post("/messages/<int:id>/<any(read,archived):status>")
@admin_only
def message_status(id, status):
    db.get_or_404(ContactMessage, id).status = status; db.session.commit(); return redirect(url_for(".messages"))

@bp.post("/messages/<int:id>/delete")
@admin_only
def message_delete(id):
    db.session.delete(db.get_or_404(ContactMessage, id)); db.session.commit(); flash("Deleted.", "success"); return redirect(url_for(".messages"))

@bp.get("/subscribers")
@admin_only
def subscribers():
    rows = [{"cells": [s.email, s.full_name or "", s.interests or "", s.subscribed_at.strftime("%d %b %Y"), "Active" if s.is_active else "Unsubscribed"], "actions":
             ([("Deactivate", url_for(".subscriber_off", id=s.id), "post", "", "")] if s.is_active else [])
             + [("Delete", url_for(".subscriber_delete", id=s.id), "post", "Erase this subscriber permanently?", "btn-danger")]}
            for s in Subscriber.query.order_by(Subscriber.subscribed_at.desc())]
    return listing("Subscribers", ["Email", "Name", "Interests", "Subscribed", "Status"], rows, export=url_for(".subscribers_csv"))

@bp.post("/subscribers/<int:id>/deactivate")
@admin_only
def subscriber_off(id):
    from ..models import utcnow
    s = db.get_or_404(Subscriber, id); s.is_active, s.unsubscribed_at = False, utcnow(); db.session.commit(); return redirect(url_for(".subscribers"))

@bp.post("/subscribers/<int:id>/delete")
@admin_only
def subscriber_delete(id):
    db.session.delete(db.get_or_404(Subscriber, id)); db.session.commit(); flash("Subscriber erased.", "success"); return redirect(url_for(".subscribers"))

def _cell(v):  # neutralise spreadsheet formula injection
    v = "" if v is None else str(v)
    return "'" + v if v and v[0] in "=+-@\t\r" else v

@bp.get("/subscribers.csv")
@admin_only
def subscribers_csv():
    out = io.StringIO(); w = csv.writer(out); w.writerow(["email", "full_name", "interests", "consent", "subscribed_at", "is_active", "unsubscribed_at"])
    for s in Subscriber.query.order_by(Subscriber.subscribed_at):
        w.writerow([_cell(x) for x in (s.email, s.full_name, s.interests, s.consent, s.subscribed_at, s.is_active, s.unsubscribed_at)])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=pcphi-subscribers.csv"})
