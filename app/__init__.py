import os
from flask import Flask, render_template, request, session
from flask_wtf.csrf import CSRFError
from markupsafe import Markup
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from . import content
from .extensions import db, migrate, csrf, login_manager
from .util import paragraphs

CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
       "script-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'")
ERRORS = {400: "Your session expired or the request was invalid. Please go back, refresh and try again.",
          403: "You do not have permission to view this page.", 404: "We could not find that page.",
          413: "That file is too large.", 429: "Too many attempts. Please wait a while and try again.",
          500: "Something went wrong on our side. Please try again shortly."}

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    if not app.config["SECRET_KEY"]: raise RuntimeError("SECRET_KEY must be set when APP_ENV=production")
    if app.config["TRUSTED_PROXIES"]:
        n = app.config["TRUSTED_PROXIES"]; app.wsgi_app = ProxyFix(app.wsgi_app, x_for=n, x_proto=n, x_host=n)
    os.makedirs(app.instance_path, exist_ok=True); os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)
    db.init_app(app); migrate.init_app(app, db); csrf.init_app(app); login_manager.init_app(app)
    login_manager.login_view, login_manager.session_protection = "admin.login", "strong"
    login_manager.login_message = "Please sign in to continue."

    from .public.routes import bp as public_bp
    from .admin.routes import bp as admin_bp
    from .cli import register
    app.register_blueprint(public_bp); app.register_blueprint(admin_bp, url_prefix="/admin"); register(app)

    g = app.jinja_env.globals
    g["icon"] = lambda n, s=22: Markup(f'<svg class="ico" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{content.ICONS[n]}</svg>')
    g["static_exists"] = lambda p: os.path.isfile(os.path.join(app.static_folder, p))
    g["c"] = content
    from .models import utcnow as now; g["now"] = now
    app.jinja_env.filters["paragraphs"] = paragraphs

    @app.context_processor
    def ctx():
        base = app.config["SITE_URL"] or request.url_root.rstrip("/")
        return {"canonical": base + request.path, "site_url": base}

    @app.after_request
    def headers(r):
        r.headers.update({"Content-Security-Policy": CSP, "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
                          "Referrer-Policy": "strict-origin-when-cross-origin", "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
                          "Cross-Origin-Opener-Policy": "same-origin"})
        if app.config["PROD"]: r.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if request.path.startswith("/admin"): r.headers["Cache-Control"] = "no-store"; r.headers["X-Robots-Tag"] = "noindex, nofollow"
        return r

    def fail(e):
        code = 400 if isinstance(e, CSRFError) else getattr(e, "code", 500)
        if code == 500: db.session.rollback()
        return render_template("error.html", code=code, msg=ERRORS.get(code, ERRORS[500])), code
    for code in ERRORS: app.register_error_handler(code, fail)
    app.register_error_handler(CSRFError, fail)
    return app
