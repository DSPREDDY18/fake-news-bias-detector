"""Pytest fixtures for the backend test suite."""
from __future__ import annotations

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend.app import create_app
from backend.extensions import db as _db
from backend.models.user import User
from backend.models.analysis import Analysis


# --------------------------------------------------------------------------- #
# Sample data
# --------------------------------------------------------------------------- #

SAMPLE_ARTICLE_TEXT = (
    "The city council voted unanimously on Tuesday to approve a new public "
    "transportation plan that would add 15 new bus routes across the metropolitan "
    "area. According to the Department of Transportation, the expansion is expected "
    "to serve an additional 50,000 daily commuters. Mayor Jane Smith said the plan "
    "represents 'a significant step forward for our city's infrastructure.' Critics, "
    "however, argue that the $200 million budget could be better spent on road repairs. "
    "The plan was developed over 18 months with input from community stakeholders and "
    "urban planning experts from the State University. A public comment period will "
    "remain open until March 15. The council's transportation committee will review "
    "feedback before final implementation begins in June."
)


# --------------------------------------------------------------------------- #
# App / DB fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture(scope='session')
def app() -> Flask:
    """Create a Flask application configured for testing."""
    application = create_app('testing')
    return application


@pytest.fixture(scope='function')
def _db_session(app: Flask):
    """Set up and tear down the database for each test function."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app: Flask, _db_session) -> FlaskClient:
    """Return a Flask test client."""
    return app.test_client()


# --------------------------------------------------------------------------- #
# User fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture()
def sample_user(app: Flask, _db_session) -> User:
    """Create and return a sample user."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('Password123')
        _db.session.add(user)
        _db.session.commit()
        # Re-query to ensure attached to session
        return User.query.filter_by(email='test@example.com').first()


@pytest.fixture()
def admin_user(app: Flask, _db_session) -> User:
    """Create and return an admin user."""
    with app.app_context():
        user = User(username='adminuser', email='admin@example.com', is_admin=True)
        user.set_password('AdminPass1')
        _db.session.add(user)
        _db.session.commit()
        return User.query.filter_by(email='admin@example.com').first()


@pytest.fixture()
def auth_headers(client: FlaskClient, sample_user: User) -> dict:
    """Return Authorization headers with a valid JWT for sample_user."""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Password123',
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture()
def admin_auth_headers(client: FlaskClient, admin_user: User) -> dict:
    """Return Authorization headers with a valid JWT for admin_user."""
    response = client.post('/api/auth/login', json={
        'email': 'admin@example.com',
        'password': 'AdminPass1',
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


# --------------------------------------------------------------------------- #
# Analysis fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture()
def sample_analysis(app: Flask, _db_session, sample_user: User) -> Analysis:
    """Create and return a sample analysis record."""
    import json
    with app.app_context():
        analysis = Analysis(
            user_id=sample_user.id,
            article_title='Test Article',
            article_text=SAMPLE_ARTICLE_TEXT,
            fake_news_score=0.85,
            fake_news_label='REAL',
            bias_score=0.1,
            bias_label='CENTER',
            sentiment_score=0.2,
            sentiment_label='NEUTRAL',
            propaganda_score=0.05,
            propaganda_techniques=json.dumps([]),
            credibility_score=82.5,
            generated_summary='A city council approved a public transportation plan.',
            gemini_explanation=json.dumps({'summary': 'Test summary'}),
            keywords=json.dumps(['transportation', 'city', 'council']),
        )
        _db.session.add(analysis)
        _db.session.commit()
        return Analysis.query.filter_by(article_title='Test Article').first()


@pytest.fixture()
def sample_text() -> str:
    """Return sample article text for analysis tests."""
    return SAMPLE_ARTICLE_TEXT
