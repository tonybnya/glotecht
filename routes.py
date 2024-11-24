"""
This file defines the routes/endpoints for the API.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Tuple, Union

from flask import Flask, Response, jsonify, render_template, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from models import Term, User


def register_routes(app: Flask, db: SQLAlchemy):
    """
    Define and register the routes/endpoints of the API,
    including the Flask-Admin interface.
    """
    # Initialize Flask-Admin
    admin = Admin(app, name="Admin Panel", template_mode='bootstrap4')

    # Add a view for the Term model
    admin.add_view(ModelView(Term, db.session))

    # Add a view for the User model
    admin.add_view(ModelView(User, db.session))


    @app.route("/")
    def index() -> Tuple[Response, Literal[200]]:
        """
        Define the endpoint for the landing page.

        Input:  Nothing
        Output: the template of the index page.
        """
        return render_template("index.html")

    @app.route("/contact")
    def contact() -> Tuple[Response, Literal[200]]:
        """
        Define the endpoint for the contact page.

        Input:  Nothing
        Output: the template of the contact page.
        """
        return render_template("contact.html")

    @app.route("/glossary")
    def glossary() -> Tuple[Response, Literal[200]]:
        """
        Define the endpoint for the glossary page.

        Input:  Nothing
        Output: the template of the glossary page.
        """
        return render_template("glossary.html")

    @app.route("/signup")
    def signup() -> Tuple[Response, Literal[200]]:
        """
        Define the endpoint for the signup page.

        Input:  Nothing
        Output: the template of the signup page.
        """
        return render_template("signup.html")

    @app.route("/login")
    def login() -> Tuple[Response, Literal[200]]:
        """
        Define the endpoint for the login page.

        Input:  Nothing
        Output: the template of the login page.
        """
        return render_template("login.html")

    @app.errorhandler(404)
    def page_not_found(e):
        """
        Define the endpoint for the glossary page.

        Input:  e   | an error
        Output: the template of the glossary page.
        """
        return render_template("404.html"), 404

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
    def create_term() -> (
        Tuple[Response, Union[Literal[201], Literal[400], Literal[500]]]
    ):
        """
        Creates a new Term in the glossary database.

        Input:  Nothing
        Output: (Response) | a JSON response with the created Term or an error message.
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
    @cross_origin()
    def get_terms() -> Tuple[Response, Union[Literal[200], Literal[404], Literal[500]]]:
        """
        Retrieves all Terms in the glossary database.

        Input:  Nothing
        Output: (Response) | a JSON response with all Terms or an error message.
        """
        try:
            # Fetch all the records of the table 'terms' in the database
            terms = Term.query.all()
            if not terms:
                return jsonify({"message": "No Terms found."}), 404

            # Create a list of dictionaries representing each term
            terms_list: List[Dict[str, Any]] = [term.to_dict() for term in terms]

            return jsonify(terms_list), 200

        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    @app.route("/api/terms/<int:tid>", methods=["GET"])
    @cross_origin()
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

    @app.route("/api/terms/search", methods=["GET"])
    @cross_origin()
    def search_terms() -> (
        Tuple[Response, Union[Literal[200], Literal[404], Literal[500]]]
    ):
        """
        Retrieves terms that match a given search string
        in either the english_term or french_term.

        Input:  Query parameter "term" | the search string to find within english_term or french_term.
        Output: (Response)             | a JSON response with matching Term(s) or an error message.
        """
        # Get the search term from the query parameters
        search_term = request.args.get("term", "").strip().lower()

        # Validate the search term
        if not search_term:
            return jsonify({"error": "Search term is required."}), 400

        try:
            # Query the database for terms where the english_term or french_term contains the search term
            terms = Term.query.filter(
                (Term.english_term.ilike(f"%{search_term}%"))
                | (Term.french_term.ilike(f"%{search_term}%"))
            ).all()

            if not terms:
                return jsonify({"message": "No matching terms found."}), 404

            # Create a list of dictionaries representing the matched terms
            terms_list: List[Dict[str, Any]] = [term.to_dict() for term in terms]

            return jsonify(terms_list), 200

        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    @app.route("/api/terms/<int:tid>", methods=["PUT"])
    def update_term(
        tid: int,
    ) -> Tuple[Response, Union[Literal[200], Literal[400], Literal[404], Literal[500]]]:
        """
        Updates an existing Term by its ID.

        Input:  (int) tid   | the ID of the term to update.
                JSON body with the fields to update.
        Output: (Response) | a JSON response with the updated Term or an error message.
        """
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
            term = Term.query.get(tid)
            if not term:
                return jsonify({"error": f"Term with ID {tid} not found."}), 404

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
    def delete_term(
        tid: int,
    ) -> Tuple[Response, Union[Literal[200], Literal[404], Literal[500]]]:
        """
        Deletes an existing Term by its ID.

        Input:  (int) tid   | the ID of the term to delete.
        Output: (Response)  | a JSON response confirming deletion or an error message.
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
    @cross_origin()
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
    @cross_origin()
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
