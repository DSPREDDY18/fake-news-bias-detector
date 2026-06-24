"""Tests for analysis endpoints."""
from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from backend.tests.conftest import SAMPLE_ARTICLE_TEXT


class TestAnalyzeText:
    """POST /api/analyze/text"""

    def test_analyze_text_success(self, client: FlaskClient) -> None:
        response = client.post('/api/analyze/text', json={
            'text': SAMPLE_ARTICLE_TEXT,
            'title': 'Transportation Plan Article',
        })
        assert response.status_code == 200
        data = response.get_json()
        analysis = data['analysis']

        # Verify all analysis components are present
        assert 'fake_news' in analysis
        assert 'label' in analysis['fake_news']
        assert analysis['fake_news']['label'] in ('REAL', 'FAKE')

        assert 'bias' in analysis
        assert 'label' in analysis['bias']
        assert analysis['bias']['label'] in ('LEFT', 'CENTER-LEFT', 'CENTER', 'CENTER-RIGHT', 'RIGHT')

        assert 'sentiment' in analysis
        assert 'label' in analysis['sentiment']
        assert analysis['sentiment']['label'] in ('POSITIVE', 'NEGATIVE', 'NEUTRAL')

        assert 'propaganda' in analysis
        assert 'score' in analysis['propaganda']
        assert 0.0 <= analysis['propaganda']['score'] <= 1.0

        assert 'credibility_score' in analysis or 'credibility' in analysis
        assert analysis.get('article_title') == 'Transportation Plan Article'

    def test_analyze_text_too_short(self, client: FlaskClient) -> None:
        response = client.post('/api/analyze/text', json={
            'text': 'Too short',
        })
        assert response.status_code == 400

    def test_analyze_text_missing(self, client: FlaskClient) -> None:
        response = client.post('/api/analyze/text', json={})
        assert response.status_code == 400

    def test_analyze_text_with_auth(self, client: FlaskClient, auth_headers: dict) -> None:
        """When authenticated, analysis should be linked to the user."""
        response = client.post('/api/analyze/text', json={
            'text': SAMPLE_ARTICLE_TEXT,
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['analysis']['user_id'] is not None

    def test_analyze_text_without_auth(self, client: FlaskClient) -> None:
        """When not authenticated, analysis should have user_id=None."""
        response = client.post('/api/analyze/text', json={
            'text': SAMPLE_ARTICLE_TEXT,
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['analysis']['user_id'] is None


class TestAnalysisHistory:
    """GET /api/analysis/history"""

    def test_history_empty(self, client: FlaskClient) -> None:
        response = client.get('/api/analysis/history')
        assert response.status_code == 200
        data = response.get_json()
        assert 'analyses' in data
        assert 'pagination' in data

    def test_history_with_data(self, client: FlaskClient, sample_analysis) -> None:
        response = client.get('/api/analysis/history')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['analyses']) >= 1

    def test_history_pagination(self, client: FlaskClient, sample_analysis) -> None:
        response = client.get('/api/analysis/history?page=1&per_page=5')
        assert response.status_code == 200
        data = response.get_json()
        assert data['pagination']['per_page'] == 5


class TestGetAnalysis:
    """GET /api/analysis/<id>"""

    def test_get_analysis_success(self, client: FlaskClient, sample_analysis) -> None:
        response = client.get(f'/api/analysis/{sample_analysis.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['analysis']['id'] == sample_analysis.id
        assert data['analysis']['article_title'] == 'Test Article'

    def test_get_analysis_not_found(self, client: FlaskClient) -> None:
        response = client.get('/api/analysis/99999')
        assert response.status_code == 404


class TestDeleteAnalysis:
    """DELETE /api/analysis/<id>"""

    def test_delete_analysis_owner(self, client: FlaskClient, auth_headers: dict, sample_analysis) -> None:
        response = client.delete(
            f'/api/analysis/{sample_analysis.id}',
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert 'deleted' in response.get_json()['message'].lower()

    def test_delete_analysis_unauthenticated(self, client: FlaskClient, sample_analysis) -> None:
        response = client.delete(f'/api/analysis/{sample_analysis.id}')
        assert response.status_code == 401

    def test_delete_analysis_not_found(self, client: FlaskClient, auth_headers: dict) -> None:
        response = client.delete('/api/analysis/99999', headers=auth_headers)
        assert response.status_code == 404
