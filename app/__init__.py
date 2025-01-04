from flask import Flask
from flask_cors import CORS
from app.routes import register_routes
from app.config import Config


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
    app.config.from_object(Config)

    register_routes(app)

    return app
