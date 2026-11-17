import os, click
from .extensions import db
from .models import AdminUser, Programme, Article
from .util import unique_slug

def register(app):
    @app.cli.command("create-admin")
    @click.option("--username", envvar="ADMIN_USERNAME", prompt=True)
    @click.option("--email", envvar="ADMIN_EMAIL", prompt=True)
    @click.option("--password", envvar="ADMIN_PASSWORD", prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option("--role", type=click.Choice(["admin", "editor"]), default="admin")
    def create_admin(username, email, password, role):
        """Create an administrator (reads ADMIN_* env vars, otherwise prompts)."""
        from flask_migrate import upgrade; upgrade()  # make sure tables exist (safe to repeat)
        if len(password) < 12: raise click.ClickException("Password must be at least 12 characters.")
        if AdminUser.query.filter((AdminUser.username == username) | (AdminUser.email == email.lower())).first():
            raise click.ClickException("A user with that username or email already exists.")
        u = AdminUser(username=username.strip(), email=email.strip().lower(), role=role); u.set_password(password)
        db.session.add(u); db.session.commit(); click.echo(f"Created {role} '{u.username}'.")

    @app.cli.command("seed-sample")
    def seed_sample():
        """Development only: add clearly labelled [SAMPLE] content. Delete it before launch."""
        p = Programme(title="[SAMPLE] Community health education drive", slug=unique_slug(Programme, "sample community health education drive"),
                      description="Sample programme used only to preview the layout. Not a real PCPHI activity.", thematic_area="Community engagement and health education",
                      status="Upcoming", published=True)
        db.session.add(p); db.session.flush()
        db.session.add(Article(title="[SAMPLE] Example update", slug=unique_slug(Article, "sample example update"), excerpt="Sample article used only to preview the layout.",
                               content="This is sample content.\n\nIt is not a real PCPHI publication.", category="Organisational announcements", published=True, programme_id=p.id))
        db.session.commit(); click.echo("Sample content added.")

    @app.cli.command("prepare-logo")
    @click.argument("src", type=click.Path(exists=True))
    def prepare_logo(src):
        """Make transparent logo, footer/mobile sizes and favicon from the supplied logo file (artwork is never altered)."""
        from PIL import Image, ImageDraw
        out = os.path.join(app.static_folder, "images", "logo"); img = Image.open(src).convert("RGBA"); img.save(os.path.join(out, "logo-original.png"))
        w, h = img.size
        for xy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            if img.getpixel(xy)[3]: ImageDraw.floodfill(img, xy, (0, 0, 0, 0), thresh=38)  # removes only background connected to the edges
        img = img.crop(img.getbbox())
        for name, px in (("logo", 640), ("logo-footer", 360), ("logo-mobile", 200)):
            r = img.copy(); r.thumbnail((px, px)); r.save(os.path.join(out, name + ".png"), optimize=True)
        s = max(img.size); sq = Image.new("RGBA", (s, s), (0, 0, 0, 0)); sq.paste(img, ((s - img.width) // 2, (s - img.height) // 2))
        sq.resize((192, 192)).save(os.path.join(out, "favicon.png")); click.echo("Logo assets written to static/images/logo/")
