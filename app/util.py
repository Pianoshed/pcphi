import os, re, secrets, unicodedata
from flask import current_app
from markupsafe import Markup, escape
from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import safe_join

Image.MAX_IMAGE_PIXELS = 40_000_000

def slugify(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:80] or "item"

def unique_slug(model, title):
    base, n, slug = slugify(title), 1, slugify(title)
    while model.query.filter_by(slug=slug).first():
        n += 1; slug = f"{base}-{n}"
    return slug

def like(term):
    return "%" + term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"

def paragraphs(text):
    """Render plain text safely: escape everything, blank line = new paragraph."""
    return Markup("".join(f"<p>{escape(p.strip())}</p>" for p in re.split(r"\n\s*\n", text or "") if p.strip()))

def save_image(f, max_px=1600):
    """Validate (real image decode), strip metadata by re-encoding, store under a random name."""
    if not isinstance(f, FileStorage) or not f.filename: return None
    try:
        img = Image.open(f.stream); img.verify(); f.stream.seek(0)
        img = Image.open(f.stream)
        if img.format not in ("JPEG", "PNG", "WEBP"): raise ValueError
        img = img.convert("RGB" if img.mode not in ("RGBA", "LA") else "RGBA")
        img.thumbnail((max_px, max_px))
    except (UnidentifiedImageError, ValueError, OSError, Image.DecompressionBombError):
        raise ValueError("Upload a valid JPG, PNG or WebP image.")
    name = secrets.token_hex(10) + ".webp"
    img.save(os.path.join(current_app.config["UPLOAD_DIR"], name), "WEBP", quality=82)
    return name

def delete_image(name):
    p = name and safe_join(current_app.config["UPLOAD_DIR"], os.path.basename(name))
    if p and os.path.isfile(p): os.remove(p)

def safe_next(url):
    return url if url and url.startswith("/") and not url.startswith("//") and "\\" not in url else None
