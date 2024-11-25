"""
This file contains the models for the database.
"""

from __future__ import annotations

from typing import Any, Dict, List

from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """
    Define a class for a User model of the glossary database.

    Attributes:
        uid (int): The primary key for the user.

        username (str): The username of the user.
        email (str): The email of the user.
        role (str): The role of the user.
    """
    # Define the name of the table in the database
    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username: str = db.Column(db.String, nullable=False)
    email: str = db.Column(db.String, nullable=False)
    password: str = db.Column(db.String, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("username", "email", name="unique_terms"),
    )

    def __repr__(self) -> str:
        """
        Returns a string representation of an User instance.

        Input:  self (User) | the User instance
        Output: the string representation of the user.
        """
        return f"User ID: {self.id} - Username: {self.username} - Email: {self.email}"

    def get_id(self) -> int:
        """
        Get an user by its ID.

        Input: self (User) | the User instance
        Output: the ID of the user.
        """
        return self.id

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts models for easier JSON serialization.

        Input:  self (User) | the User instance
        Output: a dictionary representation of the user.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }


class Term(db.Model):
    """
    Define a class for a Term model of the glossary database.
    Each Term in the glossary is represented with both English & French equivalents.

    Attributes:
        tid (int): The primary key for the term.

        domain_en (str): The domain to which all English terms belong.
        domain_fr (str): The domain to which all French terms belong.

        subdomains_en (list): Subdomains to which the English term belongs.
        subdomains_fr (list): Subdomains to which the French term belongs.

        english_term (str): The English term.
        french_term (str): The French equivalent of the English term.

        semantic_label_en (str): Semantic Label of the term in English.
        semantic_label_fr (str): Semantic Label (étiquette sémantique) of the term in French.

        variant_en (str): Variant of the term in English.
        variant_fr (str): Variant of the term in French.

        near_synonym_en (str): Near synonym of the term in English.
        near_synonym_fr (str): Near synonym of the term in French.

        definition_en (str): Definition of the term in English.
        definition_fr (str): Definition of the term in French.

        syntactic_cooccurrence_en (list): Syntactic cooccurrence information in English.
        syntactic_cooccurrence_fr (list): Syntactic cooccurrence information in French.

        lexical_relations_en (list): Lexical relationships in English.
        lexical_relations_fr (list): Lexical relationships in French.

        note_en (str): Note about the term in English.
        note_fr (str): Note about the term in French.

        not_to_be_confused_with_en (list): expression not to be confused with the term in English.
        not_to_be_confused_with_fr (list): expression not to be confused with the term in French.

        frequent_expression_en (list): Frequent expressions in English.
        frequent_expression_fr (list): Frequent expressions in French.

        phraseology_en (str): Phraseology information in English.
        phraseology_fr (str): Phraseology information in French.

        context_en (str): Context in English.
        context_fr (str): Context in French.
    """

    # Define the name of the table in the database
    __tablename__ = "terms"

    tid: int = db.Column(db.Integer, primary_key=True, autoincrement=True)

    domain_en: str = db.Column(db.String(255), nullable=False)
    domain_fr: str = db.Column(db.String(255), nullable=False)

    subdomains_en: List[str] = db.Column(db.JSON)
    subdomains_fr: List[str] = db.Column(db.JSON)

    english_term: str = db.Column(db.String(255), unique=True, nullable=False)
    french_term: str = db.Column(db.String(255), unique=True, nullable=False)

    semantic_label_en: str = db.Column(db.String(255))
    semantic_label_fr: str = db.Column(db.String(255))

    variant_en: str = db.Column(db.String(255))
    variant_fr: str = db.Column(db.String(255))

    near_synonym_en: str = db.Column(db.String(255))
    near_synonym_fr: str = db.Column(db.String(255))

    definition_en: str = db.Column(db.Text)
    definition_fr: str = db.Column(db.Text)

    syntactic_cooccurrence_en: List[str] = db.Column(db.JSON)
    syntactic_cooccurrence_fr: List[str] = db.Column(db.JSON)

    lexical_relations_en: List[Dict[str, List[str]]] = db.Column(db.JSON)
    lexical_relations_fr: List[Dict[str, List[str]]] = db.Column(db.JSON)

    note_en: str = db.Column(db.Text)
    note_fr: str = db.Column(db.Text)

    not_to_be_confused_with_en: List[str] = db.Column(db.JSON)
    not_to_be_confused_with_fr: List[str] = db.Column(db.JSON)

    frequent_expression_en: List[str] = db.Column(db.JSON)
    frequent_expression_fr: List[str] = db.Column(db.JSON)

    phraseology_en: str = db.Column(db.Text)
    phraseology_fr: str = db.Column(db.Text)

    context_en: str = db.Column(db.Text)
    context_fr: str = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("english_term", "french_term", name="unique_terms"),
    )

    def __repr__(self) -> str:
        """
        Returns a string representation of a Term instance.

        Input:  self (Term) | the Term instance
        Output: the string representation of the term.
        """
        return f"Term ID: {self.tid} - English Term: {self.english_term} - French Term: {self.french_term}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts models for easier JSON serialization.

        Input:  model (Term) | the instance of the Term
        Output: a dictionary representing the model
        """
        return {
            "tid": self.tid,
            # separator
            "domain_en": self.domain_en,
            "domain_fr": self.domain_fr,
            # separator
            "subdomains_en": self.subdomains_en,
            "subdomains_fr": self.subdomains_fr,
            # separator
            "english_term": self.english_term,
            "french_term": self.french_term,
            # separator
            "semantic_label_en": self.semantic_label_en,
            "semantic_label_fr": self.semantic_label_fr,
            # separator
            "variant_en": self.variant_en,
            "variant_fr": self.variant_fr,
            # separator
            "near_synonym_en": self.near_synonym_en,
            "near_synonym_fr": self.near_synonym_fr,
            # separator
            "definition_en": self.definition_en,
            "definition_fr": self.definition_fr,
            # separator
            "syntactic_cooccurrence_en": self.syntactic_cooccurrence_en,
            "syntactic_cooccurrence_fr": self.syntactic_cooccurrence_fr,
            # separator
            "lexical_relations_en": self.lexical_relations_en,
            "lexical_relations_fr": self.lexical_relations_fr,
            # separator
            "note_en": self.note_en,
            "note_fr": self.note_fr,
            # separator
            "not_to_be_confused_with_en": self.not_to_be_confused_with_en,
            "not_to_be_confused_with_fr": self.not_to_be_confused_with_fr,
            # separator
            "frequent_expression_en": self.frequent_expression_en,
            "frequent_expression_fr": self.frequent_expression_fr,
            # separator
            "phraseology_en": self.phraseology_en,
            "phraseology_fr": self.phraseology_fr,
            # separator
            "context_en": self.context_en,
            "context_fr": self.context_fr,
        }
