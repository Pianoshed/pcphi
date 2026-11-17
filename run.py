from app import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    if not Config.PROD:  # dev convenience; in production run `flask db upgrade` explicitly
        from flask_migrate import upgrade
        with app.app_context(): upgrade()
    app.run(debug=not Config.PROD, port=5000)
