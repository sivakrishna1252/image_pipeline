import logging
import logging.handlers
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from app.config import Config
from app.routes.gallery_routes import imagepipeline


def _setup_logging() -> None:
    Config.init_directories()

    formatter = logging.Formatter(
        fmt=Config.LOG_FORMAT,
        datefmt=Config.LOG_DATE_FORMAT,
    )

    file_handler = logging.handlers.RotatingFileHandler(
        filename=Config.LOG_FILE,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(Config.LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def create_app() -> Flask:
    _setup_logging()

    app = Flask(__name__)
    
    # Proper CORS Implementation
    CORS(app, resources={
        r"/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    app.json.sort_keys = False

    app.register_blueprint(imagepipeline)
    @app.route("/media/<path:filepath>")
    def serve_media(filepath: str):
        directory = Config.STORAGE_PATH
        return send_from_directory(directory, filepath)

    return app
