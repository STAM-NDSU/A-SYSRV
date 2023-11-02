from flask import Flask
import os
from routes import web, api
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load all env variables
load_dotenv()


def create_app():
    # Init Flask app
    app = Flask(
        __name__,
        template_folder="./web/views/",
        static_folder="./web/static/",
        static_url_path="/static/",
    )

    # Setup app configuration
    def setup_config():
        # Load the default configuration
        app.config.from_object("config.default")

        # Load .env variables
        for key, value in os.environ.items():
            app.config[key] = value

    setup_config()

    return app


# Configure logging
def configure_logging():
    logger = logging.getLogger()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        "storage/logs/app.log", backupCount=100, maxBytes=1000000
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


# Register blueprints
def register_blueprints():
    with app.app_context():
        app.register_blueprint(web.bp)
        app.register_blueprint(api.bp)


# Run application
app = create_app()
configure_logging()
register_blueprints()

