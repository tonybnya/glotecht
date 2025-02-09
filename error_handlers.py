from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException


def register_error_handlers(app, db):
    @app.errorhandler(404)
    def not_found_error(error):
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify({"error": "Not found"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # Roll back db session in case of error
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify({"error": "Internal server error"}), 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify(
                {
                    "code": e.code,
                    "name": e.name,
                    "description": e.description,
                }
            ), e.code
        return render_template("errors/generic.html", error=e), e.code
