# PCPHI website

Flask single-repo site for the Participative Care Public Health Initiative: public site, `/subscribe`, enquiry forms and a lightweight admin.
Stack: Flask, Flask-SQLAlchemy, Flask-WTF (CSRF), Flask-Login, Flask-Migrate, Pillow. No JS framework.

## Run locally
```
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # macOS/Linux: cp .env.example .env
flask db upgrade                # creates the database tables
flask create-admin             # prompts for username, email, password (min 12 chars)
python run.py                  # serves http://127.0.0.1:5000
```
Optional: `flask seed-sample` adds clearly labelled **[SAMPLE]** programme/article for previewing layouts. Delete them in the admin before launch.

## Add your brand and photos (not supplied with the brief)
- **Done:** logo, hero photo (Children's Day), About-page photos, address, email and social links are in place. Social URLs use standard patterns for the handle `participativecare`; check each opens the right page (LinkedIn may be `/company/` or `/in/`) and edit `SOCIAL` in `app/content.py`. Set `SITE_URL=https://www.participativecare.org.ng` in production.
- **Logo (how it was made):** `flask prepare-logo path\to\logo.png` creates the transparent logo, footer/mobile sizes and favicon in `app/static/images/logo/` (only background connected to the image edge is removed; artwork is untouched). Until then a text wordmark is shown.
- **Hero photo:** save an authentic, licensed photo as `app/static/images/hero/hero.jpg` (about 1000x1250, under 250 KB) and update `hero_alt` in `app/content.py` to describe it accurately.
- Programme and article images are uploaded in the admin (validated, re-encoded to WebP, max 1600px, metadata stripped).

## Editing content
Organisation text, the six goals, nine thematic areas, values, pathways and the optional `IMPACT` figures are in `app/content.py`. `IMPACT` is empty on purpose: add only verified figures and the section will display them.
The values listed on the About page are drawn from the supplied vision, mission and goals; confirm them with PCPHI.

## Admin
`/admin/login`. Roles: **admin** (everything, including messages, subscribers, CSV export, deletions) and **editor** (programmes and articles only; cannot delete).
Create more users with `flask create-admin --role editor`. Article and programme text is plain text (blank line = new paragraph), which is escaped on output.

## Email (optional)
Set `SMTP_*` variables. With no SMTP configured the site never claims an email was sent; subscriptions are still stored. Every outgoing subscriber email must include the per-subscriber link from `Subscriber.token()` (`/unsubscribe/<token>`).

## Deploy on Render
1. Push this repo to GitHub, then create a Blueprint from `render.yaml` (web service + PostgreSQL + disk), or create the same pieces manually.
2. Set `SITE_URL` to your public URL. `SECRET_KEY` is generated for you; `APP_ENV=production` enables secure cookies, HSTS and proxy headers and refuses to start without a secret.
3. After the first deploy open the Render shell and run `flask create-admin`.
4. Uploaded images need a persistent disk (`UPLOAD_DIR`) or external object storage; the container filesystem is wiped on each deploy.

Other hosts: `pip install -r requirements-postgres.txt && flask db upgrade` then `gunicorn run:app`.

## PostgreSQL
Models are portable. Run `pip install -r requirements-postgres.txt` (adds the psycopg 3 driver; not needed for SQLite), set `DATABASE_URL=postgresql://user:pass@host/db` (`postgres://` URLs are rewritten automatically), then `flask db upgrade`. To move existing SQLite data, export subscribers from the admin CSV and re-import, or use `pgloader`.
After changing models: `flask db migrate -m "message"` then `flask db upgrade`; review the generated migration first.

## Security notes
CSRF on every POST; scrypt password hashing; sessions HttpOnly, SameSite=Lax, Secure in production, 2-hour lifetime; login throttled per IP and per username (5 failures / 15 min); honeypot plus per-IP limits on public forms; strict Content-Security-Policy (no inline scripts or styles), clickjacking, nosniff and referrer headers; admin pages `no-store` and `noindex`; uploads decoded and re-encoded with Pillow, served from a non-executable route; CSV export neutralises spreadsheet formulas; unsubscribe links are signed tokens; errors are generic.
The rate limiter is in-memory per worker; use a shared store (e.g. Redis) if you scale to many instances. Fonts load from Google Fonts; to avoid third-party requests, self-host them and remove the two Google domains from `CSP` in `app/__init__.py`.
