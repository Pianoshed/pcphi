import smtplib
from email.message import EmailMessage
from flask import current_app

def send_mail(to, subject, body):
    """Return True only if an SMTP server is configured AND accepted the message."""
    c = current_app.config["SMTP"]
    if not (c["host"] and c["from"]): return False
    try:
        m = EmailMessage(); m["From"], m["To"], m["Subject"] = c["from"], to, subject; m.set_content(body)
        with smtplib.SMTP(c["host"], int(c["port"] or 587), timeout=10) as s:
            s.starttls()
            if c["user"]: s.login(c["user"], c["password"] or "")
            s.send_message(m)
        return True
    except Exception:
        current_app.logger.exception("SMTP send failed")
        return False
