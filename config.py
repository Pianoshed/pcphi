import os, secrets
from datetime import timedelta
from dotenv import load_dotenv

BASE = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE, ".env"))
_env = os.environ.get

def _db():
    url = _env("DATABASE_URL") or "sqlite:///" + os.path.join(BASE, "instance", "pcphi.db")
    for old in ("postgres://", "postgresql://"):  # use the psycopg 3 driver (only needed for PostgreSQL)
        if url.startswith(old): return "postgresql+psycopg://" + url[len(old):]
    return url

class Config:
    PROD = _env("APP_ENV", "development") == "production"
    SECRET_KEY = _env("SECRET_KEY") or (None if PROD else secrets.token_hex(32))
    SQLALCHEMY_DATABASE_URI = _db()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SITE_URL = (_env("SITE_URL") or "").rstrip("/")
    UPLOAD_DIR = _env("UPLOAD_DIR") or os.path.join(BASE, "instance", "uploads")
    TRUSTED_PROXIES = int(_env("TRUSTED_PROXIES", "1" if PROD else "0"))
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = PROD
    REMEMBER_COOKIE_SECURE = PROD
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    WTF_CSRF_TIME_LIMIT = 7200
    SMTP = {k: _env("SMTP_" + k.upper()) for k in ("host", "port", "user", "password", "from")}
