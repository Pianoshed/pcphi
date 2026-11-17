from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SelectField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from . import content as c

class _Base(FlaskForm):
    website = StringField()  # honeypot: real visitors never see or fill this

class LoginForm(FlaskForm):
    username = StringField("Username", [DataRequired(), Length(max=64)])
    password = PasswordField("Password", [DataRequired(), Length(max=128)])

class SubscribeForm(_Base):
    full_name = StringField("Full name", [Optional(), Length(max=120)])
    email = StringField("Email address", [DataRequired(), Email(), Length(max=254)])
    interests = SelectMultipleField("Areas of interest", choices=[(i, i) for i in c.INTERESTS], validators=[Optional()])
    consent = BooleanField("I agree that PCPHI may email me updates and that I can unsubscribe at any time.", [DataRequired(message="Please confirm your consent to subscribe.")])

class ContactForm(_Base):
    name = StringField("Your name", [DataRequired(), Length(max=120)])
    email = StringField("Email address", [DataRequired(), Email(), Length(max=254)])
    subject = StringField("Subject", [DataRequired(), Length(max=150)])
    message = TextAreaField("Message", [DataRequired(), Length(min=10, max=3000)])

class EnquiryForm(_Base):
    name = StringField("Your name", [DataRequired(), Length(max=120)])
    email = StringField("Email address", [DataRequired(), Email(), Length(max=254)])
    message = TextAreaField("How would you like to be involved?", [DataRequired(), Length(min=10, max=2000)])

_img = [FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only (JPG, PNG, WebP).")]

class ProgrammeForm(FlaskForm):
    title = StringField("Title", [DataRequired(), Length(max=200)])
    description = TextAreaField("Description (blank line = new paragraph)", [DataRequired(), Length(max=20000)])
    thematic_area = SelectField("Thematic area", choices=[(t[0], t[0]) for t in c.THEMES])
    status = SelectField("Status", choices=[(s, s) for s in c.STATUSES])
    location = StringField("Location (only if verified)", [Optional(), Length(max=150)])
    start_date = DateField("Start date", [Optional()])
    end_date = DateField("End date", [Optional()])
    image = FileField("Featured image", _img)
    published = BooleanField("Published (visible on the website)")
    def validate_end_date(self, f):
        if f.data and self.start_date.data and f.data < self.start_date.data: raise ValidationError("End date is before the start date.")

class ArticleForm(FlaskForm):
    title = StringField("Title", [DataRequired(), Length(max=200)])
    excerpt = StringField("Short summary", [DataRequired(), Length(max=300)])
    content = TextAreaField("Content (blank line = new paragraph)", [DataRequired(), Length(max=50000)])
    category = SelectField("Category", choices=[(x, x) for x in c.CATEGORIES])
    programme_id = SelectField("Related programme", coerce=int, validate_choice=False)
    featured_image = FileField("Featured image", _img)
    published = BooleanField("Published (visible on the website)")
