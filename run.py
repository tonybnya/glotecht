"""
This file runs the application.
"""

from __future__ import annotations

from flask import Flask

from app import create_app

# Create an instance of the Flask application
flask_app: Flask = create_app()

if __name__ == "__main__":
    # Run the application in debug mode
    flask_app.run(host="0.0.0.0", debug=True, port=5003)
