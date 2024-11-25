"""
This file defines the routes/endpoints for the API.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Tuple, Union

from flask import Flask, Response, jsonify, render_template, request, redirect, url_for, flash
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_required, login_user, logout_user
from flask_bcrypt import Bcrypt

from models import Term, User


def admin_required(f: Callable) -> Callable:
    """Decorator to require admin access for a route."""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


class SecureAdminIndexView(AdminIndexView):
    """Secure admin index that requires authentication."""
    
    @expose('/')
    # @admin_required
    def index(self):
        return super().index()


class SecureModelView(ModelView):
    """Base secure model view that requires authentication."""
    
    def is_accessible(self) -> bool:
        return current_user.is_authenticated

    def inaccessible_callback(self, name: str, **kwargs: Any) -> Response:
        return redirect(url_for('login', next=request.url))


class UserAdminView(SecureModelView):
    """Admin interface for User model."""
    column_list = ['id', 'username', 'email']
    column_searchable_list = ['username', 'email']
    form_excluded_columns = ['password']
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50

    def on_model_change(self, form: Any, model: User, is_created: bool) -> None:
        """Hash password when creating/editing users through admin."""
        if is_created or form.password.data:
            model.password = Bcrypt().generate_password_hash(
                form.password.data.encode('utf-8')
            ).decode('utf-8')


class TermAdminView(SecureModelView):
    """Admin interface for Term model."""
    column_list = ['tid', 'english_term', 'french_term', 'domain_en', 'domain_fr']
    column_searchable_list = ['english_term', 'french_term']
    column_filters = ['domain_en', 'domain_fr']
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50


def register_routes(app: Flask, db: SQLAlchemy, bcrypt: Bcrypt) -> None:
    """Register all routes and admin views."""
    
    # Initialize Flask-Admin with secure index
    admin = Admin(
        app,
        name="GloTechT - Panneau d'Administration",
        template_mode='bootstrap4',
        index_view=SecureAdminIndexView()
    )

    # Add secure model views
    admin.add_view(UserAdminView(User, db.session, name='Administrateurs'))
    admin.add_view(TermAdminView(Term, db.session, name='Termes'))

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

    @app.route("/api/terms/search", methods=["GET"])
    @cross_origin()
    def search_terms() -> Tuple[Response, int]:
        """Public API endpoint for searching terms."""
        query = request.args.get("q", "").lower()
        if not query:
            return jsonify([]), 200

        try:
            terms = Term.query.all()
            results = []
            
            for term in terms:
                if (query in term.english_term.lower() or 
                    query in term.french_term.lower() or
                    query in term.domain_en.lower() or
                    query in term.domain_fr.lower()):
                    results.append(term.to_dict())
            
            return jsonify(results), 200
            
        except Exception as e:
            app.logger.error(f"Search error: {str(e)}")
            return jsonify({"error": "An error occurred during search"}), 500

    # Admin-only routes
    @app.route("/login", methods=["GET", "POST"])
    def login() -> Union[str, Response]:
        """Admin login page."""
        if current_user.is_authenticated:
            return redirect(url_for('admin.index'))

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

            password_bytes = password.encode('utf-8')
            if bcrypt.check_password_hash(user.password, password_bytes):
                login_user(user)
                next_page = request.args.get('next')
                if next_page and not next_page.startswith('/'):
                    next_page = None
                return redirect(next_page or url_for('admin.index'))
            
            flash("Email ou mot de passe incorrect", "error")
            return render_template("login.html"), 401
            
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            flash("Une erreur s'est produite", "error")
            return render_template("login.html"), 500

    @app.route("/signup", methods=["GET", "POST"])
    # @admin_required
    def signup() -> Union[str, Response]:
        """Route to create new admin users."""
        if request.method == "GET":
            if current_user.is_authenticated:
                return redirect(url_for('admin.index'))
            return render_template("signup.html")
        
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        if not all([username, email, password, password_confirm]):
            flash("Tous les champs sont obligatoires", "error")
            return render_template("signup.html"), 400
            
        if password != password_confirm:
            flash("Les mots de passe ne correspondent pas", "error")
            return render_template("signup.html"), 400

        if User.query.filter_by(email=email).first():
            flash("Cet email existe déjà", "error")
            return render_template("signup.html"), 400

        try:
            password_bytes = password.encode('utf-8')
            hashed_password = bcrypt.generate_password_hash(password_bytes).decode('utf-8')
            
            user = User(
                username=username,
                email=email,
                password=hashed_password
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash("Administrateur créé avec succès", "success")
            return redirect(url_for('admin.index'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Signup error: {str(e)}")
            flash("Une erreur s'est produite", "error")
            return render_template("signup.html"), 500

    @app.route("/logout")
    # @admin_required
    def logout() -> Response:
        """Admin logout."""
        logout_user()
        return redirect(url_for('index'))

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
                    "EN": "English-French Glossary for Disruptive Technologies (Big Data, AI, Blockchain).",
                    "FR": "Glossaire Anglais-Francais des technologies transformatrices (Big Data, IA, blockchain)."
                }
            ),
            200,
        )


    ################################################
    # TERM ROUTES
    ################################################

    @app.route("/api/terms", methods=["POST"])
    # @admin_required
    def create_term() -> (
        Tuple[Response, Union[Literal[201], Literal[400], Literal[500]]]
    ):
        """
        Creates a new Term in the glossary database.
        Only admins can create terms.
        """
        # Get the JSON data from the request body
        data = request.get_json()

        # Validate the presence of required data
        if not data:
            return jsonify({"error": "Invalid JSON data."}), 400

        english_term: str = data.get("english_term")
        french_term: str = data.get("french_term")

        if not english_term:
            return jsonify({"error": "English Term is required."}), 400
        if not french_term:
            return jsonify({"error": "French Term is required."}), 400

        # Validate data types of the the required fields
        if not isinstance(english_term, str) or not isinstance(french_term, str):
            return (
                jsonify(
                    {
                        "error": "Invalid data types: English and French terms should be strings."
                    }
                ),
                400,
            )

        term: Term = Term(
            domain_en=data.get("domain_en"),
            domain_fr=data.get("domain_fr"),
            subdomains_en=data.get("subdomains_en"),
            subdomains_fr=data.get("subdomains_fr"),
            english_term=english_term.strip(),
            french_term=french_term.strip(),
            semantic_label_en=data.get("semantic_label_en"),
            semantic_label_fr=data.get("semantic_label_fr"),
            variant_en=data.get("variant_en"),
            variant_fr=data.get("variant_fr"),
            near_synonym_en=data.get("near_synonym_en"),
            near_synonym_fr=data.get("near_synonym_fr"),
            definition_en=data.get("definition_en"),
            definition_fr=data.get("definition_fr"),
            syntactic_cooccurrence_en=data.get("syntactic_cooccurrence_en"),
            syntactic_cooccurrence_fr=data.get("syntactic_cooccurrence_fr"),
            lexical_relations_en=data.get("lexical_relations_en"),
            lexical_relations_fr=data.get("lexical_relations_fr"),
            note_en=data.get("note_en"),
            note_fr=data.get("note_fr"),
            not_to_be_confused_with_en=data.get("not_to_be_confused_with_en"),
            not_to_be_confused_with_fr=data.get("not_to_be_confused_with_fr"),
            frequent_expression_en=data.get("frequent_expression_en"),
            frequent_expression_fr=data.get("frequent_expression_fr"),
            phraseology_en=data.get("phraseology_en"),
            phraseology_fr=data.get("phraseology_fr"),
            context_en=data.get("context_en"),
            context_fr=data.get("context_fr"),
        )

        try:
            # Add the term to the session
            db.session.add(term)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return (
                jsonify({"error": "This term already exists."}),
                400,
            )
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

        return (
            jsonify({"message": "Term created successfully!", "term": term.to_dict()}),
            201,
        )

    @app.route("/api/terms", methods=["GET"])
    def get_terms() -> Tuple[Response, Literal[200]]:
        """
        Get all terms from the glossary database.
        Public endpoint - no authentication required.
        """
        terms = Term.query.all()
        return jsonify([term.to_dict() for term in terms]), 200

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

    @app.route("/api/terms/<int:tid>", methods=["PUT"])
    # @admin_required
    def update_term(
        tid: int,
    ) -> Tuple[Response, Union[Literal[200], Literal[400], Literal[404], Literal[500]]]:
        """
        Update a term in the glossary database.
        Only admins can update terms.
        """
        term = Term.query.get(tid)
        if not term:
            return jsonify({"error": "Term not found"}), 404

        # Get the JSON data from the request body
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        # Validate required fields
        english_term: str = data.get("english_term")
        french_term: str = data.get("french_term")

        if not english_term:
            return jsonify({"error": "English Term is required."}), 400
        if not french_term:
            return jsonify({"error": "French Term is required."}), 400

        if english_term is not None and not isinstance(english_term, str):
            return (
                jsonify(
                    {"error": "Invalid data type: English term should be a string."}
                ),
                400,
            )
        if french_term is not None and not isinstance(french_term, str):
            return (
                jsonify(
                    {"error": "Invalid data type: French term should be a string."}
                ),
                400,
            )

        try:
            # Update the term fields
            if english_term is not None:
                term.english_term = english_term.strip()
            if french_term is not None:
                term.french_term = french_term.strip()

            if "domain_en" in data:
                term.domain_en = data.get("domain_en")
            if "domain_fr" in data:
                term.domain_fr = data.get("domain_fr")

            if "subdomains_en" in data:
                term.subdomains_en = data.get("subdomains_en")
            if "subdomains_fr" in data:
                term.subdomains_fr = data.get("subdomains_fr")

            if "semantic_label_en" in data:
                term.semantic_label_en = data.get("semantic_label_en")
            if "semantic_label_fr" in data:
                term.semantic_label_fr = data.get("semantic_label_fr")

            if "variant_en" in data:
                term.variant_en = data.get("variant_en")
            if "variant_fr" in data:
                term.variant_fr = data.get("variant_fr")

            if "near_synonym_en" in data:
                term.near_synonym_en = data.get("near_synonym_en")
            if "near_synonym_fr" in data:
                term.near_synonym_fr = data.get("near_synonym_fr")

            if "definition_en" in data:
                term.definition_en = data.get("definition_en")
            if "definition_fr" in data:
                term.definition_fr = data.get("definition_fr")

            if "syntactic_cooccurrence_en" in data:
                term.syntactic_cooccurrence_en = data.get("syntactic_cooccurrence_en")
            if "syntactic_cooccurrence_fr" in data:
                term.syntactic_cooccurrence_fr = data.get("syntactic_cooccurrence_fr")

            if "lexical_relations_en" in data:
                term.lexical_relations_en = data.get("lexical_relations_en")
            if "lexical_relations_fr" in data:
                term.lexical_relations_fr = data.get("lexical_relations_fr")

            if "note_en" in data:
                term.note_en = data.get("note_en")
            if "note_fr" in data:
                term.note_fr = data.get("note_fr")

            if "not_to_be_confused_with_en" in data:
                term.not_to_be_confused_with_en = data.get("not_to_be_confused_with_en")
            if "not_to_be_confused_with_fr" in data:
                term.not_to_be_confused_with_fr = data.get("not_to_be_confused_with_fr")

            if "frequent_expression_en" in data:
                term.frequent_expression_en = data.get("frequent_expression_en")
            if "frequent_expression_fr" in data:
                term.frequent_expression_fr = data.get("frequent_expression_fr")

            if "phraseology_en" in data:
                term.phraseology_en = data.get("phraseology_en")
            if "phraseology_fr" in data:
                term.phraseology_fr = data.get("phraseology_fr")

            if "context_en" in data:
                term.context_en = data.get("context_en")
            if "context_fr" in data:
                term.context_fr = data.get("context_fr")

            db.session.commit()

            return (
                jsonify(
                    {"message": "Term updated successfully!", "term": term.to_dict()}
                ),
                200,
            )
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Integrity error occurred."}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    @app.route("/api/terms/<int:tid>", methods=["DELETE"])
    # @admin_required
    def delete_term(
        tid: int,
    ) -> Tuple[Response, Union[Literal[200], Literal[404], Literal[500]]]:
        """
        Delete a term from the glossary database.
        Only admins can delete terms.
        """
        try:
            term = Term.query.get(tid)
            if not term:
                return jsonify({"error": f"Term with ID {tid} not found."}), 404

            db.session.delete(term)
            db.session.commit()

            return jsonify({"message": "Term deleted successfully!"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


    ################################################
    # USER ROUTES
    ################################################

    @app.route("/api/users", methods=["POST"])
    # @admin_required
    def create_user() -> (
        Tuple[Response, Union[Literal[201], Literal[400], Literal[500]]]
    ):
        """
        Creates a new User in the glossary database.

        Input:  Nothing
        Output: (Response) | a JSON response with the created User or an error message.
        """
        # Get the JSON data from the request body
        data = request.get_json()

        # Validate the presence of required data
        if not data:
            return jsonify({"error": "Invalid JSON data."}), 400

        username: str = data.get("username")
        email: str = data.get("email")
        password: str = data.get("password")
        role: str = data.get("role")

        if not username:
            return jsonify({"error": "Username is required."}), 400
        if not email:
            return jsonify({"error": "Email is required."}), 400
        if not password:
            return jsonify({"error": "Password is required."}), 400
        if not role:
            return jsonify({"error": "Role is required."}), 400

        # Validate data types of the the required fields
        if not isinstance(username, str) or not isinstance(email, str) or not isinstance(password, str)or not isinstance(role, str):
            return (
                jsonify(
                    {
                        "error": "Invalid data types: Username, email, and role should be strings."
                    }
                ),
                400,
            )

        user: User = User(
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
            role=data.get("role"),
        )

        try:
            # Add the user to the session
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return (
                jsonify({"error": "This User already exists."}),
                400,
            )
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

        return (
            jsonify({"message": "User created successfully!", "user": user.to_dict()}),
            201,
        )

    @app.route("/api/users", methods=["GET"])
    # @admin_required
    def get_users() -> Tuple[Response, Union[Literal[200], Literal[404], Literal[500]]]:
        """
        Retrieves all Users in the glossary database.

        Input:  Nothing
        Output: (Response) | a JSON response with all Users or an error message.
        """
        try:
            # Fetch all the records of the table 'users' in the database
            users = User.query.all()
            if not users:
                return jsonify({"message": "No Users found."}), 404

            # Create a list of dictionaries representing each term
            users_list: List[Dict[str, Any]] = [user.to_dict() for user in users]

            return jsonify(users_list), 200

        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    @app.route("/api/users/<int:uid>", methods=["GET"])
    # @admin_required
    def get_user(
        uid: int,
    ) -> Tuple[Response, Union[Literal[200], Literal[404], Literal[500]]]:
        """
        Retrieves a single User by its ID.

        Input:  (int) uid   | the ID of the User to retrieve.
        Output: (Response)  | a JSON response with the User details or an error message.
        """
        try:
            # Fetch the User with the given User ID
            user = User.query.get(uid)
            if not user:
                return jsonify({"error": f"User with ID {uid} not found."}), 404

            return jsonify(user.to_dict()), 200

        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    @app.route("/api/users/<int:uid>", methods=["PUT"])
    # @admin_required
    def update_user(
        uid: int,
    ) -> Tuple[Response, Union[Literal[200], Literal[400], Literal[404], Literal[500]]]:
        """
        Updates an existing User by its ID.

        Input:  (int) uid   | the ID of the user to update.
                JSON body with the fields to update.
        Output: (Response) | a JSON response with the updated User or an error message.
        """
        # Get the JSON data from the request body
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        # Validate required fields
        username: str = data.get("username")
        email: str = data.get("email")
        password: str = data.get("password")
        role: str = data.get("role")

        if not username:
            return jsonify({"error": "Username is required."}), 400
        if not email:
            return jsonify({"error": "Email is required."}), 400
        if not password:
            return jsonify({"error": "Password is required."}), 400
        if not role:
            return jsonify({"error": "Role is required."}), 400

        if username is not None and not isinstance(username, str):
            return (
                jsonify(
                    {"error": "Invalid data type: Username should be a string."}
                ),
                400,
            )
        if email is not None and not isinstance(email, str):
            return (
                jsonify(
                    {"error": "Invalid data type: Email should be a string."}
                ),
                400,
            )
        if password is not None and not isinstance(password, str):
            return (
                jsonify(
                    {"error": "Invalid data type: Password should be a string."}
                ),
                400,
            )
        if role is not None and not isinstance(role, str):
            return (
                jsonify(
                    {"error": "Invalid data type: Role should be a string."}
                ),
                400,
            )

        try:
            user = User.query.get(uid)
            if not user:
                return jsonify({"error": f"User with ID {uid} not found."}), 404

            # Update the term fields
            if username is not None:
                user.username = username.strip()
            if email is not None:
                user.email = email.strip()
            if password is not None:
                user.password = password.strip()
            if role is not None:
                user.role = role.strip()

            db.session.commit()

            return (
                jsonify(
                    {"message": "User updated successfully!", "user": user.to_dict()}
                ),
                200,
            )
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Integrity error occurred."}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    @app.route("/api/users/<int:uid>", methods=["DELETE"])
    # @admin_required
    def delete_user(
        uid: int,
    ) -> Tuple[Response, Union[Literal[200], Literal[404], Literal[500]]]:
        """
        Deletes an existing User by its ID.

        Input:  (int) uid   | the ID of the user to delete.
        Output: (Response)  | a JSON response confirming deletion or an error message.
        """
        try:
            user = User.query.get(uid)
            if not user:
                return jsonify({"error": f"User with ID {uid} not found."}), 404

            db.session.delete(user)
            db.session.commit()

            return jsonify({"message": "User deleted successfully!"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    @app.route("/update_password/<int:user_id>", methods=["POST"])
    @login_required
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
            if not bcrypt.check_password_hash(user.password, old_password.encode('utf-8')):
                flash("Le mot de passe actuel est incorrect", "error")
                return render_template("update_password.html"), 401

            password_bytes = new_password.encode('utf-8')
            hashed_password = bcrypt.generate_password_hash(password_bytes).decode('utf-8')
            user.password = hashed_password
            
            db.session.commit()
            flash("Mot de passe mis à jour avec succès", "success")
            return redirect(url_for('admin.index'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Password update error: {str(e)}")
            flash("Une erreur s'est produite", "error")
            return render_template("update_password.html"), 500

    @app.route("/update_password_form")
    @login_required
    def update_password_form() -> str:
        """Display the password update form."""
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter pour modifier votre mot de passe", "error")
            return redirect(url_for('login'))
        return render_template("update_password.html")

    @app.errorhandler(404)
    def page_not_found(e):
        """404 - Not Found page."""
        return render_template("404.html"), 404
