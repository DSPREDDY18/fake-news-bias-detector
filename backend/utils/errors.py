"""Custom exception classes and error handler registration."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify


class APIError(Exception):
    """Base API error.

    All custom API exceptions inherit from this class so that the
    global error handler can catch them uniformly.
    """

    status_code: int = 500
    message: str = 'An unexpected error occurred.'

    def __init__(self, message: Optional[str] = None, status_code: Optional[int] = None, payload: Optional[dict] = None) -> None:
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the error for JSON response."""
        body: Dict[str, Any] = {
            'error': True,
            'status_code': self.status_code,
            'message': self.message,
        }
        if self.payload:
            body['details'] = self.payload
        return body


class ValidationError(APIError):
    """Raised when user input fails validation."""

    status_code = 400
    message = 'Validation error.'


class NotFoundError(APIError):
    """Raised when a requested resource does not exist."""

    status_code = 404
    message = 'Resource not found.'


class AuthenticationError(APIError):
    """Raised when authentication fails."""

    status_code = 401
    message = 'Authentication failed.'


def register_error_handlers(app: Flask) -> None:
    """Register global JSON error handlers on the Flask application.

    Handles custom APIError subclasses as well as common HTTP errors
    so every response from the API is consistently shaped.

    Args:
        app: The Flask application instance.
    """

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError) -> Tuple[Any, int]:
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response, error.status_code

    @app.errorhandler(400)
    def handle_bad_request(error: Any) -> Tuple[Any, int]:
        return jsonify({
            'error': True,
            'status_code': 400,
            'message': 'Bad request.',
        }), 400

    @app.errorhandler(401)
    def handle_unauthorized(error: Any) -> Tuple[Any, int]:
        return jsonify({
            'error': True,
            'status_code': 401,
            'message': 'Unauthorized. Please provide valid credentials.',
        }), 401

    @app.errorhandler(403)
    def handle_forbidden(error: Any) -> Tuple[Any, int]:
        return jsonify({
            'error': True,
            'status_code': 403,
            'message': 'Forbidden. You do not have permission to access this resource.',
        }), 403

    @app.errorhandler(404)
    def handle_not_found(error: Any) -> Tuple[Any, int]:
        return jsonify({
            'error': True,
            'status_code': 404,
            'message': 'The requested resource was not found.',
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error: Any) -> Tuple[Any, int]:
        return jsonify({
            'error': True,
            'status_code': 405,
            'message': 'Method not allowed.',
        }), 405

    @app.errorhandler(413)
    def handle_payload_too_large(error: Any) -> Tuple[Any, int]:
        return jsonify({
            'error': True,
            'status_code': 413,
            'message': 'Payload too large. Maximum content length exceeded.',
        }), 413

    @app.errorhandler(422)
    def handle_unprocessable(error: Any) -> Tuple[Any, int]:
        return jsonify({
            'error': True,
            'status_code': 422,
            'message': 'Unprocessable entity.',
        }), 422

    @app.errorhandler(429)
    def handle_rate_limit(error: Any) -> Tuple[Any, int]:
        return jsonify({
            'error': True,
            'status_code': 429,
            'message': 'Too many requests. Please slow down.',
        }), 429

    @app.errorhandler(500)
    def handle_internal_error(error: Any) -> Tuple[Any, int]:
        import traceback
        tb = traceback.format_exc()
        app.logger.error('Internal server error: %s\n%s', error, tb)
        resp = {
            'error': True,
            'status_code': 500,
            'message': 'Internal server error.',
        }
        # Include traceback in non-production for debugging
        if app.debug or app.config.get('TESTING'):
            resp['traceback'] = str(error)
        return jsonify(resp), 500
