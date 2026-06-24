"""Analysis routes (Firebase Firestore backend).

Blueprint: analysis
Prefix:    /api

Endpoints:
    POST   /analyze/text       — analyze raw article text
    POST   /analyze/url        — extract & analyze an article from URL
    GET    /analysis/history   — paginated analysis history
    GET    /analysis/<id>      — single analysis detail
    DELETE /analysis/<id>      — delete an analysis (JWT required)
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request

from backend.services.firebase_service import FirebaseAnalysisService, FirebaseUserService
from backend.services.article_extractor import ArticleExtractor
from backend.services.bias_detector import BiasDetector
from backend.services.credibility_scorer import CredibilityScorer
from backend.services.fake_news_detector import FakeNewsDetector
from backend.services.gemini_service import GeminiService
from backend.services.propaganda_detector import PropagandaDetector
from backend.services.sentiment_analyzer import SentimentAnalyzer
from backend.utils.errors import NotFoundError, ValidationError
from backend.utils.validators import validate_article_text, validate_url

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api')

# Service singletons (lazy-init to avoid heavy model loading at import time)
_fake_news_detector: Optional[FakeNewsDetector] = None
_bias_detector: Optional[BiasDetector] = None
_sentiment_analyzer: Optional[SentimentAnalyzer] = None
_propaganda_detector: Optional[PropagandaDetector] = None
_credibility_scorer: Optional[CredibilityScorer] = None
_gemini_service: Optional[GeminiService] = None
_article_extractor: Optional[ArticleExtractor] = None


def _get_services() -> tuple:
    """Lazily initialise and return all analysis services."""
    global _fake_news_detector, _bias_detector, _sentiment_analyzer
    global _propaganda_detector, _credibility_scorer, _gemini_service
    global _article_extractor

    if _fake_news_detector is None:
        _fake_news_detector = FakeNewsDetector()
    if _bias_detector is None:
        _bias_detector = BiasDetector()
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    if _propaganda_detector is None:
        _propaganda_detector = PropagandaDetector()
    if _credibility_scorer is None:
        _credibility_scorer = CredibilityScorer()
    if _gemini_service is None:
        _gemini_service = GeminiService()
    if _article_extractor is None:
        _article_extractor = ArticleExtractor()

    return (
        _fake_news_detector, _bias_detector, _sentiment_analyzer,
        _propaganda_detector, _credibility_scorer, _gemini_service,
        _article_extractor,
    )


def _get_optional_user_id() -> Optional[int]:
    """Return the current user's id if a valid JWT is present, else None."""
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return int(identity) if identity else None
    except Exception:
        return None


def _run_analysis(text: str, title: str = 'Untitled', url: Optional[str] = None) -> Dict[str, Any]:
    """Execute the full analysis pipeline and persist to Firebase.

    Args:
        text: Validated article text.
        title: Article title.
        url: Optional source URL.

    Returns:
        The serialised analysis dict.
    """
    (
        fake_detector, bias_detector, sentiment_analyzer,
        propaganda_detector, credibility_scorer, gemini_svc,
        _extractor,
    ) = _get_services()

    # 1. Fake news detection
    fake_result = fake_detector.analyze(text)

    # 2. Bias detection
    bias_result = bias_detector.analyze(text)

    # 3. Sentiment analysis
    sentiment_result = sentiment_analyzer.analyze(text)

    # 4. Propaganda detection
    propaganda_result = propaganda_detector.analyze(text)

    # 5. Credibility score
    credibility_result = credibility_scorer.calculate(
        fake_result, bias_result, sentiment_result, propaganda_result, text,
    )

    # 6. Gemini AI analysis (non-blocking, graceful failure)
    scores_dict = {
        'fake_news': fake_result,
        'bias': bias_result,
        'sentiment': sentiment_result,
        'propaganda': propaganda_result,
        'credibility': credibility_result,
    }
    try:
        gemini_result = gemini_svc.generate_full_analysis(text, scores_dict)
    except Exception as exc:
        logger.warning('Gemini full analysis failed: %s', exc)
        gemini_result = {
            'summary': gemini_svc._fallback_summary(text),
            'bias_explanation': '',
            'misinformation': '',
            'fact_checks': '',
            'overall_assessment': '',
        }

    # 7. Determine user (optional)
    user_id = _get_optional_user_id()

    # 8. Persist to Firebase Firestore
    analysis_data = {
        'user_id': user_id,
        'article_title': title,
        'article_text': text,
        'article_url': url,
        'fake_news_score': fake_result.get('confidence', 0.0),
        'fake_news_label': fake_result.get('label', 'UNKNOWN'),
        'bias_score': bias_result.get('score', 0.0),
        'bias_label': bias_result.get('label', 'CENTER'),
        'sentiment_score': sentiment_result.get('score', 0.0),
        'sentiment_label': sentiment_result.get('label', 'NEUTRAL'),
        'propaganda_score': propaganda_result.get('score', 0.0),
        'propaganda_techniques': json.dumps(propaganda_result.get('techniques', [])),
        'credibility_score': credibility_result.get('score', 0.0),
        'generated_summary': gemini_result.get('summary', ''),
        'gemini_explanation': json.dumps(gemini_result),
        'keywords': json.dumps(fake_result.get('keywords', [])),
    }

    analysis = FirebaseAnalysisService.create_analysis(analysis_data)

    # 9. Build response
    result = dict(analysis)
    result['credibility'] = credibility_result
    result['fake_news'] = {
        'label': fake_result.get('label', 'UNKNOWN'),
        'confidence': fake_result.get('confidence', 0.0),
        'features': fake_result.get('features', {}),
    }
    result['bias'] = {
        'label': bias_result.get('label', 'CENTER'),
        'score': bias_result.get('score', 0.0),
        'indicators': bias_result.get('indicators', []),
        'confidence': bias_result.get('confidence', 0.0),
    }
    result['sentiment'] = {
        'label': sentiment_result.get('label', 'NEUTRAL'),
        'score': sentiment_result.get('score', 0.0),
        'breakdown': sentiment_result.get('breakdown', {}),
        'confidence': sentiment_result.get('confidence', 0.0),
    }
    result['propaganda'] = {
        'score': propaganda_result.get('score', 0.0),
        'techniques': propaganda_result.get('techniques', []),
    }

    return result


# ------------------------------------------------------------------ #
# POST /api/analyze/text
# ------------------------------------------------------------------ #
@analysis_bp.route('/analyze/text', methods=['POST'])
def analyze_text():
    """Analyze raw article text.

    Request JSON:
        {
          "text": "...",
          "title": "..."       (optional)
        }

    Returns:
        200: full analysis result
    """
    data = request.get_json(silent=True) or {}
    text = validate_article_text(data.get('text'))
    title = (data.get('title') or 'Untitled').strip()[:500]

    result = _run_analysis(text, title=title)
    return jsonify({'message': 'Analysis complete.', 'analysis': result}), 200


# ------------------------------------------------------------------ #
# POST /api/analyze/url
# ------------------------------------------------------------------ #
@analysis_bp.route('/analyze/url', methods=['POST'])
def analyze_url():
    """Extract an article from a URL and analyze it.

    Request JSON:
        {
          "url": "https://..."
        }

    Returns:
        200: full analysis result
    """
    data = request.get_json(silent=True) or {}
    url = validate_url(data.get('url'))

    (_fnd, _bd, _sa, _pd, _cs, _gs, article_extractor) = _get_services()

    try:
        extracted = article_extractor.extract(url)
    except ValueError as exc:
        raise ValidationError(str(exc))

    text = extracted['text']
    title = extracted.get('title', 'Untitled')

    result = _run_analysis(text, title=title, url=url)
    result['extracted'] = {
        'authors': extracted.get('authors', []),
        'publish_date': extracted.get('publish_date'),
        'top_image': extracted.get('top_image'),
    }

    return jsonify({'message': 'Analysis complete.', 'analysis': result}), 200


# ------------------------------------------------------------------ #
# GET /api/analysis/history
# ------------------------------------------------------------------ #
@analysis_bp.route('/analysis/history', methods=['GET'])
def analysis_history():
    """Return paginated analysis history.

    Query params:
        page (int, default=1)
        per_page (int, default=20, max=100)

    If a valid JWT is provided, shows only that user's analyses.
    Otherwise, shows all analyses.
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    user_id = _get_optional_user_id()

    result = FirebaseAnalysisService.get_history(
        user_id=user_id, page=page, per_page=per_page,
    )

    return jsonify(result), 200


# ------------------------------------------------------------------ #
# GET /api/analysis/<id>
# ------------------------------------------------------------------ #
@analysis_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id: int):
    """Return a single analysis by ID.

    Returns:
        200: { analysis: {...} }
        404: not found
    """
    analysis = FirebaseAnalysisService.get_by_id(analysis_id)
    if analysis is None:
        raise NotFoundError(f'Analysis with id {analysis_id} not found.')

    return jsonify({'analysis': analysis}), 200


# ------------------------------------------------------------------ #
# DELETE /api/analysis/<id>
# ------------------------------------------------------------------ #
@analysis_bp.route('/analysis/<int:analysis_id>', methods=['DELETE'])
@jwt_required()
def delete_analysis(analysis_id: int):
    """Delete an analysis (must be owner or admin).

    Returns:
        200: { message: "..." }
        404: not found
    """
    analysis = FirebaseAnalysisService.get_by_id(analysis_id)
    if analysis is None:
        raise NotFoundError(f'Analysis with id {analysis_id} not found.')

    user_id = int(get_jwt_identity())

    # Only the owner or an admin can delete
    user = FirebaseUserService.get_by_id(user_id)
    if analysis.get('user_id') != user_id and (user is None or not user.get('is_admin')):
        raise ValidationError('You do not have permission to delete this analysis.', status_code=403)

    FirebaseAnalysisService.delete_by_id(analysis_id)

    return jsonify({'message': 'Analysis deleted successfully.'}), 200
