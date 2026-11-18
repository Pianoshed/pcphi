import smtplib
from email.message import EmailMessage
from flask import current_app

def send_mail(to, subject, body):
    """Return True only if an SMTP server is configured AND accepted the message.
    Works with Resend: SMTP_HOST=smtp.resend.com, SMTP_USER=resend, SMTP_PASSWORD=<API key>,
    SMTP_PORT=465 (implicit SSL) or 587/2587 (STARTTLS); SMTP_FROM must use a domain verified in Resend."""
    c = current_app.config["SMTP"]
    if not (c["host"] and c["from"]): return False
    try:
        m = EmailMessage(); m["From"], m["To"], m["Subject"] = c["from"], to, subject; m.set_content(body)
        port = int(c["port"] or 587)
        if port in (465, 2465):
            s = smtplib.SMTP_SSL(c["host"], port, timeout=15)
        else:
            s = smtplib.SMTP(c["host"], port, timeout=15); s.starttls()
        with s:
            if c["user"]: s.login(c["user"], c["password"] or "")
            s.send_message(m)
        return True
    except Exception:
        current_app.logger.exception("SMTP send failed")
        return False
