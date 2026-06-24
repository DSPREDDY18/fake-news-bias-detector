"""Flask application factory and entry point.

Usage:
    from backend.app import create_app
    app = create_app('development')
    app.run()
"""
from __future__ import annotations

import os
import click
from flask import Flask

from backend.config import config_by_name
from backend.extensions import jwt, cors
from backend.routes import register_blueprints
from backend.utils.errors import register_error_handlers
from backend.utils.logger import setup_logging


def create_app(config_name: str | None = None) -> Flask:
    """Application factory.

    Args:
        config_name: One of 'development', 'testing', 'production'.
                     Defaults to the FLASK_ENV env var or 'development'.

    Returns:
        A fully configured Flask application instance.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # ---- Extensions -------------------------------------------------- #
    jwt.init_app(app)
    cors.init_app(app, resources={r'/api/*': {'origins': '*'}})

    # ---- Blueprints -------------------------------------------------- #
    register_blueprints(app)

    # ---- Error handlers ---------------------------------------------- #
    register_error_handlers(app)

    # ---- Logging ----------------------------------------------------- #
    if not app.config.get('TESTING'):
        setup_logging(app)

    # ---- Firebase initialisation ------------------------------------- #
    with app.app_context():
        try:
            from backend.services.firebase_service import get_db
            get_db()
            app.logger.info('Firebase Firestore connected successfully.')
        except Exception as exc:
            app.logger.warning('Firebase init deferred: %s', exc)

    # ---- Ensure reports directory exists ------------------------------ #
    reports_dir = app.config.get('REPORTS_DIR', os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'reports',
    ))
    os.makedirs(reports_dir, exist_ok=True)

    # ---- CLI commands ------------------------------------------------ #
    _register_cli_commands(app)

    # ---- Health-check route ------------------------------------------ #
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'message': 'Fake News & Bias Detector API is running.', 'database': 'Firebase Firestore'}, 200

    return app


def _register_cli_commands(app: Flask) -> None:
    """Register custom Flask CLI commands."""

    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    def create_admin(username: str, email: str, password: str) -> None:
        """Create an admin user in Firebase.

        Usage:
            flask create-admin <username> <email> <password>
        """
        from werkzeug.security import generate_password_hash
        from backend.services.firebase_service import FirebaseUserService

        if FirebaseUserService.get_by_email(email):
            click.echo(f'Error: A user with email "{email}" already exists.')
            return

        if FirebaseUserService.get_by_username(username):
            click.echo(f'Error: A user with username "{username}" already exists.')
            return

        password_hash = generate_password_hash(password)
        user = FirebaseUserService.create_user(
            username=username, email=email,
            password_hash=password_hash, is_admin=True,
        )
        click.echo(f'Admin user "{username}" created successfully (id={user["id"]}).')


# ------------------------------------------------------------------ #
# Entry point
# ------------------------------------------------------------------ #
if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=True)
