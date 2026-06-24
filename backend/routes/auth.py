"""Authentication routes (Firebase Firestore backend).

Blueprint: auth
Prefix:    /api/auth

Endpoints:
    POST /register  — create a new user account
    POST /login     — authenticate and receive a JWT
    GET  /me        — get the current user's profile (JWT required)
    POST /logout    — logout (JWT required)
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from backend.services.firebase_service import FirebaseUserService
from backend.utils.errors import AuthenticationError, ValidationError
from backend.utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _user_to_dict(user: dict) -> dict:
    """Return a safe user dict (no password_hash)."""
    return {
        'id': user.get('id'),
        'username': user.get('username'),
        'email': user.get('email'),
        'is_admin': user.get('is_admin', False),
        'created_at': user.get('created_at'),
    }


# ------------------------------------------------------------------ #
# POST /api/auth/register
# ------------------------------------------------------------------ #
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user.

    Request JSON:
        {
          "username": "...",
          "email": "...",
          "password": "..."
        }

    Returns:
        201: { user: {...}, access_token: "..." }
    """
    data = request.get_json(silent=True) or {}

    username = (data.get('username') or '').strip()
    if not username or len(username) < 3:
        raise ValidationError('Username must be at least 3 characters.')
    if len(username) > 80:
        raise ValidationError('Username must not exceed 80 characters.')

    email = validate_email(data.get('email'))
    password = validate_password(data.get('password'))

    if FirebaseUserService.get_by_username(username):
        raise ValidationError('Username is already taken.')
    if FirebaseUserService.get_by_email(email):
        raise ValidationError('Email is already registered.')

    password_hash = generate_password_hash(password)
    user = FirebaseUserService.create_user(
        username=username, email=email,
        password_hash=password_hash, is_admin=False,
    )

    access_token = create_access_token(identity=str(user['id']))

    return jsonify({
        'message': 'User registered successfully.',
        'user': _user_to_dict(user),
        'access_token': access_token,
    }), 201


# ------------------------------------------------------------------ #
# POST /api/auth/login
# ------------------------------------------------------------------ #
@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return a JWT.

    Request JSON:
        {
          "email": "...",
          "password": "..."
        }

    Returns:
        200: { user: {...}, access_token: "..." }
    """
    data = request.get_json(silent=True) or {}

    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        raise AuthenticationError('Email and password are required.')

    user = FirebaseUserService.get_by_email(email)
    if user is None or not check_password_hash(user.get('password_hash', ''), password):
        raise AuthenticationError('Invalid email or password.')

    access_token = create_access_token(identity=str(user['id']))

    return jsonify({
        'message': 'Login successful.',
        'user': _user_to_dict(user),
        'access_token': access_token,
    }), 200


# ------------------------------------------------------------------ #
# GET /api/auth/me
# ------------------------------------------------------------------ #
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Return the authenticated user's profile.

    Returns:
        200: { user: {...} }
    """
    user_id = int(get_jwt_identity())
    user = FirebaseUserService.get_by_id(user_id)
    if user is None:
        raise AuthenticationError('User not found.')

    return jsonify({'user': _user_to_dict(user)}), 200


# ------------------------------------------------------------------ #
# POST /api/auth/logout
# ------------------------------------------------------------------ #
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint.

    In a stateless JWT system the client simply discards the token.
    This endpoint exists for API completeness and could be extended
    with a token blocklist.

    Returns:
        200: { message: "..." }
    """
    return jsonify({'message': 'Successfully logged out.'}), 200
