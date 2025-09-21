from flask import Flask

from config import Config


def create_app() -> Flask:
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Register blueprints
    from .main import main as main_bp
    app.register_blueprint(main_bp)

    return app

