"""
This file defines the routes/endpoints for the API.
"""

from __future__ import annotations

from functools import wraps
from io import StringIO
import csv
from typing import Any, Callable, Literal, Tuple, Union
import re

from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_required, login_user, logout_user
from flask_bcrypt import Bcrypt
from sqlalchemy import func
from sqlalchemy import exists, select
from sqlalchemy import text

from models import Term, User


def admin_required(f: Callable) -> Callable:
    """Decorator to require admin access for a route."""

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not current_user.is_authenticated:
            return redirect(url_for("login", next=request.url))
        if not current_user.is_admin():
            flash("Accès administrateur requis", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


class SecureAdminIndexView(AdminIndexView):
    """Secure admin index that requires authentication."""

    @expose("/")
    @admin_required
    def index(self):
        """Render the admin index page with user context."""
        # Get the current user's information
        user_info = {"username": current_user.username, "email": current_user.email}

        # Get counts for dashboard
        users_count = User.query.count()
        terms_count = Term.query.count()

        return self.render(
            "admin/index.html",
            user_info=user_info,
            users_count=users_count,
            terms_count=terms_count,
        )

    @expose("/logout")
    def logout(self):
        """Custom logout route for admin panel."""
        logout_user()
        return redirect(url_for("index"))

    @expose("/update-password")
    @login_required
    def update_password_view(self):
        """Redirect to password update form."""
        return redirect(url_for("update_password_form"))


class SecureModelView(ModelView):
    """Base secure model view that requires authentication."""

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

    def inaccessible_callback(self, name: str, **kwargs: Any) -> Response:
        return redirect(url_for("login", next=request.url))


class UserAdminView(SecureModelView):
    """Admin interface for User model."""

    column_list = ["id", "username", "email"]
    column_searchable_list = ["username", "email"]
    column_filters = ["username", "email"]
    form_excluded_columns = ["password"]
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50

    def on_model_change(self, form: Any, model: User, is_created: bool) -> None:
        """Hash password when creating/editing users through admin."""
        if is_created or form.password.data:
            model.password = (
                Bcrypt()
                .generate_password_hash(form.password.data.encode("utf-8"))
                .decode("utf-8")
            )


class TermAdminView(SecureModelView):
    """Admin interface for Term model."""

    column_list = [
        "tid",
        "english_term",
        "french_term",
        "subdomains_en",
        "subdomains_fr",
    ]
    column_searchable_list = ["english_term", "french_term", "domain_en", "domain_fr"]
    column_filters = [
        "domain_en",
        "domain_fr",
        "semantic_label_en",
        "semantic_label_fr",
    ]
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50


def register_routes(app: Flask, db: SQLAlchemy, bcrypt: Bcrypt) -> None:
    """Register all routes and admin views."""

    # Initialize Flask-Admin with secure index
    admin = Admin(
        app,
        name="GloTechT",
        template_mode="bootstrap4",
        index_view=SecureAdminIndexView(name="Tableau de bord"),
        # index_view=SecureAdminIndexView()
    )

    # Add secure model views
    admin.add_view(UserAdminView(User, db.session, name="Administrateurs"))
    admin.add_view(TermAdminView(Term, db.session, name="Termes"))

    # Public routes
    @app.route("/")
    def index() -> str:
        """Landing page."""
        return render_template("index.html")

    @app.route("/glossary")
    def glossary() -> str:
        """Glossary page."""
        return render_template("glossary.html")

    @app.route("/contact")
    def contact() -> str:
        """Contact page."""
        return render_template("contact.html")

    @app.route("/docs")
    def docs() -> str:
        """Documentation page."""
        return render_template("docs.html")

    @app.route("/semantic-labels")
    def semantic_labels() -> str:
        """Semantic labels page."""
        return render_template("semantic_labels.html")

    @app.route("/terms-list")
    def terms_list() -> str:
        """Terms list page."""
        return render_template("terms_list.html")

    @app.route("/api/terms/search", methods=["GET"])
    @cross_origin()
    def search_terms() -> Tuple[Response, int]:
        """Public API endpoint for searching terms."""
        query = request.args.get("q", "").strip()
        search_type = request.args.get("type", "term")

        if not query:
            return jsonify([]), 200

        try:
            base_query = Term.query

            if search_type == "term":
                base_query = base_query.filter(
                    db.or_(
                        Term.english_term.ilike(f"%{query}%"),
                        Term.french_term.ilike(f"%{query}%")
                    )
                )
            elif search_type == "class":
                base_query = base_query.filter(
                    db.or_(
                        Term.semantic_label_en.ilike(f"%{query}%"),
                        Term.semantic_label_fr.ilike(f"%{query}%")
                    )
                )
            elif search_type == "synonym":
                base_query = base_query.filter(
                    db.or_(
                        Term.synonym_en.ilike(f"%{query}%"),
                        Term.synonym_fr.ilike(f"%{query}%"),
                        Term.near_synonym_en.ilike(f"%{query}%"),
                        Term.near_synonym_fr.ilike(f"%{query}%")
                    )
                )
            elif search_type == "subdomain":
                # For array fields in SQLite, use json_each with EXISTS and text() for explicit SQL
                base_query = base_query.filter(
                    db.or_(
                        exists(select(1).select_from(func.json_each(Term.subdomains_en)).where(text("lower(value) LIKE lower(:query)"))),
                        exists(select(1).select_from(func.json_each(Term.subdomains_fr)).where(text("lower(value) LIKE lower(:query)")))
                    )
                ).params(query=f"%{query}%") # Bind the query parameter once for both EXISTS clauses

            results = [term.to_dict() for term in base_query.all()]
            return jsonify(results), 200

        except Exception as e:
            app.logger.error(f"Search error: {str(e)}")
            return jsonify({"error": f"An error occurred during search: {str(e)}"}), 500

    # Admin-only routes
    @app.route("/login", methods=["GET", "POST"])
    def login() -> Union[str, Response]:
        """Admin login page."""
        if current_user.is_authenticated:
            return redirect(url_for("admin.index"))

        if request.method == "GET":
            return render_template("login.html")

        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email et mot de passe requis", "error")
            return render_template("login.html"), 400

        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                flash("Email ou mot de passe incorrect", "error")
                return render_template("login.html"), 401

            password_bytes = password.encode("utf-8")
            if bcrypt.check_password_hash(user.password, password_bytes):
                login_user(user)
                next_page = request.args.get("next")
                if next_page and not next_page.startswith("/"):
                    next_page = None
                return redirect(next_page or url_for("admin.index"))

            flash("Email ou mot de passe incorrect", "error")
            return render_template("login.html"), 401

        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            flash("Une erreur s'est produite", "error")
            return render_template("login.html"), 500

    @app.route("/logout")
    def logout() -> Response:
        """Admin logout."""
        logout_user()
        return redirect(url_for("index"))

    @app.route("/api")
    def root() -> Tuple[Response, Literal[200]]:
        """
        Define the default (root) endpoint "/".

        Input:  Nothing
        Output: a dictionary message
        """
        return (
            jsonify(
                {
                    "EN": "English-French Glossary of Terms Related to Disruptive Technologies (Big Data • AI • Blockchain).",
                    "FR": "Glossaire anglais-francais de termes relatifs aux technologies transformatrices (Big Data • AI • Blockchain).",
                }
            ),
            200,
        )

    @app.route("/api/terms", methods=["GET"])
    def get_terms() -> Tuple[Response, Literal[200]]:
        """
        Get all terms from the glossary database.
        Public endpoint - no authentication required.
        """
        terms = Term.query.all()
        return jsonify([term.to_dict() for term in terms]), 200

    @app.route("/api/terms/xml", methods=["GET"])
    def get_terms_xml() -> Response:
        """Get all terms in XML format."""
        terms = Term.query.all()
        
        # Create XML structure
        xml_data = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_data.append('<terms>')
        
        for term in terms:
            xml_data.append('  <term>')
            term_dict = term.to_dict()
            for key, value in term_dict.items():
                if value:  # Only include non-None values
                    # Escape special characters and wrap in CDATA if needed
                    if isinstance(value, str) and any(char in value for char in '<>&'):
                        value = f'<![CDATA[{value}]]>'
                    xml_data.append(f'    <{key}>{value}</{key}>')
            xml_data.append('  </term>')
        
        xml_data.append('</terms>')
        
        # Join all lines and create response
        xml_content = '\n'.join(xml_data)
        response = Response(xml_content, mimetype='application/xml')
        response.headers['Content-Disposition'] = 'attachment; filename=glotecht_terms.xml'
        
        return response

    @app.route("/update_password/<int:user_id>", methods=["POST"])
    def update_password(user_id: int) -> Response:
        """Update user password with proper hashing."""
        try:
            if current_user.id != user_id:
                return jsonify({"error": "Unauthorized"}), 403

            old_password = request.form.get("old_password")
            new_password = request.form.get("new_password")

            if not old_password or not new_password:
                flash("Les deux mots de passe sont requis", "error")
                return render_template("update_password.html"), 400

            user = User.query.get(user_id)
            if not user:
                flash("Utilisateur non trouvé", "error")
                return render_template("update_password.html"), 404

            # Verify old password
            if not bcrypt.check_password_hash(
                user.password, old_password.encode("utf-8")
            ):
                flash("Le mot de passe actuel est incorrect", "error")
                return render_template("update_password.html"), 401

            password_bytes = new_password.encode("utf-8")
            hashed_password = bcrypt.generate_password_hash(password_bytes).decode(
                "utf-8"
            )
            user.password = hashed_password

            db.session.commit()
            flash("Mot de passe mis à jour avec succès", "success")
            return redirect(url_for("admin.index"))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Password update error: {str(e)}")
            flash("Une erreur s'est produite", "error")
            return render_template("update_password.html"), 500

    @app.route("/update_password_form")
    def update_password_form() -> str:
        """Display the password update form."""
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter pour modifier votre mot de passe", "error")
            return redirect(url_for("login"))
        return render_template("update_password.html")

    @app.errorhandler(404)
    def page_not_found(e):
        """404 - Not Found page."""
        return render_template("404.html"), 404

    @app.route("/api/terms/list", methods=["GET"])
    def get_terms_list():
        try:
            # Query all terms and return all details, ordered by english_term
            terms = Term.query.order_by(Term.english_term).all()
            terms_list = [term.to_dict() for term in terms]
            return jsonify(terms_list), 200
        except Exception as e:
            app.logger.error(f"Error retrieving terms list: {str(e)}")
            return jsonify({"error": "Failed to retrieve terms list"}), 500

    @app.route("/api/terms/semantic-labels", methods=["GET"])
    def get_semantic_labels():
        try:
            # Query only the semantic labels, ordered by English label
            labels = db.session.query(
                Term.semantic_label_en,
                Term.semantic_label_fr
            ).filter(
                Term.semantic_label_en.isnot(None),  # Filter out NULL values
                Term.semantic_label_fr.isnot(None)
            ).distinct().order_by(Term.semantic_label_en).all()
            
            # Helper to strip trailing [ ... ] and whitespace
            def clean_label(label):
                if not label:
                    return ""
                return re.sub(r"\s*\[.*\]$", "", label).strip()

            # Deduplicate by English label only
            seen_en = set()
            labels_list = []
            for label in labels:
                en_clean = clean_label(label.semantic_label_en)
                fr_clean = clean_label(label.semantic_label_fr)
                if en_clean.lower() not in seen_en:
                    seen_en.add(en_clean.lower())
                    labels_list.append({
                        "EN": en_clean,
                        "FR": fr_clean
                    })
            
            return jsonify(labels_list), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/terms/csv")
    def get_terms_csv() -> Response:
        """Get all terms in CSV format."""
        terms = Term.query.all()
        
        # Convert to list of dictionaries
        terms_list = [term.to_dict() for term in terms]
        
        if not terms_list:
            return Response("No terms found", mimetype='text/csv')
        
        # Get headers from the first term
        headers = list(terms_list[0].keys())
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        
        # Write headers and data
        writer.writeheader()
        writer.writerows(terms_list)
        
        # Create response
        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=glotecht_terms.csv'
        
        return response

    @app.route("/api/terms/<int:tid>", methods=["GET"])
    def get_term(
        tid: int,
    ) -> Tuple[Response, Union[Literal[200], Literal[404], Literal[500]]]:
        """
        Retrieves a single Term by its ID.

        Input:  (int) tid   | the ID of the term to retrieve.
        Output: (Response)  | a JSON response with the Term details or an error message.
        """
        try:
            # Fetch the Term with the given term ID
            term = Term.query.get(tid)
            if not term:
                return jsonify({"error": f"Term with ID {tid} not found."}), 404

            return jsonify(term.to_dict()), 200

        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500