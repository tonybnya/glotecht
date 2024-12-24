"""
This file creates the application.
"""

from __future__ import annotations

import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Define a database object
db: SQLAlchemy = SQLAlchemy()


def create_app() -> Flask:
    """
    Create the Flask app and return it as an object.

    Input:  Nothing
    Output: an object representing the Flask application
    """
    # Define the Flask application
    app: Flask = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/",
    )

    # Define a string for the SQLite database
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance', 'glossary.db'))}"

    # Suppress warning related to the SQLALCHEMY_TRACK_MODIFICATIONS
    # configuration option in Flask-SQLAlchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Set a secret key for session management
    app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')

    # Initialize CORS
    CORS(app)

    # Initialize the Flask application
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    bcrypt = Bcrypt(app)

    from models import User  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # import register_routes here to avoid circular imports
    from routes import register_routes

    register_routes(app, db, bcrypt)

    migrate: Migrate = Migrate(app, db)  # noqa: F841

    return app