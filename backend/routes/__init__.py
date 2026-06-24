"""Routes package — registers all API blueprints."""
from __future__ import annotations

from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Import and register all route blueprints on the application.

    Args:
        app: The Flask application instance.
    """
    from backend.routes.auth import auth_bp
    from backend.routes.analysis import analysis_bp
    from backend.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(reports_bp)
