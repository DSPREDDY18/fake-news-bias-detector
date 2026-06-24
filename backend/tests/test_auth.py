"""Tests for authentication endpoints."""
from __future__ import annotations

import pytest
from flask.testing import FlaskClient


class TestRegistration:
    """POST /api/auth/register"""

    def test_register_success(self, client: FlaskClient) -> None:
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Secure123',
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'new@example.com'
        assert 'access_token' in data
        assert 'password_hash' not in data['user']

    def test_register_missing_username(self, client: FlaskClient) -> None:
        response = client.post('/api/auth/register', json={
            'email': 'no_user@example.com',
            'password': 'Secure123',
        })
        assert response.status_code == 400

    def test_register_short_username(self, client: FlaskClient) -> None:
        response = client.post('/api/auth/register', json={
            'username': 'ab',
            'email': 'short@example.com',
            'password': 'Secure123',
        })
        assert response.status_code == 400

    def test_register_invalid_email(self, client: FlaskClient) -> None:
        response = client.post('/api/auth/register', json={
            'username': 'gooduser',
            'email': 'notanemail',
            'password': 'Secure123',
        })
        assert response.status_code == 400

    def test_register_weak_password_no_digit(self, client: FlaskClient) -> None:
        response = client.post('/api/auth/register', json={
            'username': 'gooduser',
            'email': 'good@example.com',
            'password': 'NoDigits',
        })
        assert response.status_code == 400

    def test_register_weak_password_too_short(self, client: FlaskClient) -> None:
        response = client.post('/api/auth/register', json={
            'username': 'gooduser',
            'email': 'good@example.com',
            'password': 'Ab1',
        })
        assert response.status_code == 400

    def test_register_duplicate_email(self, client: FlaskClient, sample_user) -> None:
        response = client.post('/api/auth/register', json={
            'username': 'otheruser',
            'email': 'test@example.com',
            'password': 'Secure123',
        })
        assert response.status_code == 400
        assert 'already registered' in response.get_json()['message'].lower()

    def test_register_duplicate_username(self, client: FlaskClient, sample_user) -> None:
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'unique@example.com',
            'password': 'Secure123',
        })
        assert response.status_code == 400
        assert 'already taken' in response.get_json()['message'].lower()


class TestLogin:
    """POST /api/auth/login"""

    def test_login_success(self, client: FlaskClient, sample_user) -> None:
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Password123',
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['email'] == 'test@example.com'
        assert 'access_token' in data

    def test_login_wrong_password(self, client: FlaskClient, sample_user) -> None:
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPass1',
        })
        assert response.status_code == 401

    def test_login_nonexistent_email(self, client: FlaskClient) -> None:
        response = client.post('/api/auth/login', json={
            'email': 'nobody@example.com',
            'password': 'Whatever1',
        })
        assert response.status_code == 401

    def test_login_missing_fields(self, client: FlaskClient) -> None:
        response = client.post('/api/auth/login', json={})
        assert response.status_code == 401


class TestProtectedRoutes:
    """GET /api/auth/me and POST /api/auth/logout"""

    def test_me_authenticated(self, client: FlaskClient, auth_headers: dict) -> None:
        response = client.get('/api/auth/me', headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['user']['email'] == 'test@example.com'

    def test_me_unauthenticated(self, client: FlaskClient) -> None:
        response = client.get('/api/auth/me')
        assert response.status_code == 401

    def test_logout(self, client: FlaskClient, auth_headers: dict) -> None:
        response = client.post('/api/auth/logout', headers=auth_headers)
        assert response.status_code == 200
        assert 'logged out' in response.get_json()['message'].lower()

    def test_logout_unauthenticated(self, client: FlaskClient) -> None:
        response = client.post('/api/auth/logout')
        assert response.status_code == 401
