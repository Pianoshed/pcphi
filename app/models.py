from datetime import datetime, timezone
from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeSerializer, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager

def utcnow(): return datetime.now(timezone.utc).replace(tzinfo=None)

class Stamped:
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

class Edited(Stamped):
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

class AdminUser(UserMixin, Stamped, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), default="editor", nullable=False)  # admin | editor
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    __table_args__ = (db.CheckConstraint("role in ('admin','editor')", name="ck_user_role"),)
    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

class Programme(Edited, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    thematic_area = db.Column(db.String(80), nullable=False, index=True)
    image = db.Column(db.String(80))
    status = db.Column(db.String(10), default="Upcoming", nullable=False, index=True)
    location = db.Column(db.String(150))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    articles = db.relationship("Article", back_populates="programme")
    __table_args__ = (db.CheckConstraint("status in ('Upcoming','Ongoing','Completed')", name="ck_prog_status"),)

class Article(Edited, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    excerpt = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), nullable=False, index=True)
    featured_image = db.Column(db.String(80))
    published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    programme_id = db.Column(db.Integer, db.ForeignKey("programme.id", ondelete="SET NULL"))
    programme = db.relationship("Programme", back_populates="articles")

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    interests = db.Column(db.String(300), default="", nullable=False)
    consent = db.Column(db.Boolean, default=False, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    unsubscribed_at = db.Column(db.DateTime)
    def _ser(self): return URLSafeSerializer(current_app.config["SECRET_KEY"], salt="unsubscribe")
    def token(self): return self._ser().dumps(self.id)
    @classmethod
    def from_token(cls, token):
        try: return db.session.get(cls, cls._ser(cls).loads(token))
        except BadSignature: return None

class ContactMessage(Stamped, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), default="new", nullable=False, index=True)
    __table_args__ = (db.CheckConstraint("status in ('new','read','archived')", name="ck_msg_status"),)

@login_manager.user_loader
def load_user(uid):
    u = db.session.get(AdminUser, int(uid))
    return u if u and u.is_active else None
