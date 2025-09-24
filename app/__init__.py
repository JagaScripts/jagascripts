from flask import Flask

from config import Config


def create_app() -> Flask:
    # Disable the default app-level static route to avoid collisions
    app = Flask(__name__, static_folder=None)

    # Load configuration
    app.config.from_object(Config)

    # Register blueprints
    from .main import main as main_bp
    app.register_blueprint(main_bp)

    return app

