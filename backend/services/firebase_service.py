"""Firebase Firestore service.

Provides CRUD operations for Users, Analyses, and Reports
using Google Cloud Firestore as the database backend.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

# Singleton app reference
_firebase_app: Optional[firebase_admin.App] = None
_db = None


def get_db():
    """Get Firestore client, initializing Firebase if needed."""
    global _firebase_app, _db

    if _db is not None:
        return _db

    cred_path = os.getenv(
        'FIREBASE_CREDENTIALS_PATH',
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)
        ))), 'firebase-credentials.json')
    )

    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f'Firebase credentials not found at {cred_path}. '
            'Set FIREBASE_CREDENTIALS_PATH env var or place firebase-credentials.json in project root.'
        )

    if _firebase_app is None:
        cred = credentials.Certificate(cred_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info('Firebase initialized successfully.')

    _db = firestore.client()
    return _db


# ──────────────────────────────────────────────────────────────────────────────
# Users Collection
# ──────────────────────────────────────────────────────────────────────────────

class FirebaseUserService:
    """CRUD operations for the 'users' collection."""

    COLLECTION = 'users'

    @staticmethod
    def create_user(username: str, email: str, password_hash: str,
                    is_admin: bool = False) -> Dict[str, Any]:
        db = get_db()
        now = datetime.now(timezone.utc).isoformat()
        # Auto-increment ID
        counter_ref = db.collection('counters').document('users')
        counter = counter_ref.get()
        new_id = (counter.to_dict().get('next_id', 1)) if counter.exists else 1
        counter_ref.set({'next_id': new_id + 1})

        user_data = {
            'id': new_id,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'is_admin': is_admin,
            'created_at': now,
        }
        db.collection(FirebaseUserService.COLLECTION).document(str(new_id)).set(user_data)
        logger.info('Created user %s (id=%d)', username, new_id)
        return user_data

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        db = get_db()
        doc = db.collection(FirebaseUserService.COLLECTION).document(str(user_id)).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        docs = db.collection(FirebaseUserService.COLLECTION) \
            .where('email', '==', email).limit(1).stream()
        for doc in docs:
            return doc.to_dict()
        return None

    @staticmethod
    def get_by_username(username: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        docs = db.collection(FirebaseUserService.COLLECTION) \
            .where('username', '==', username).limit(1).stream()
        for doc in docs:
            return doc.to_dict()
        return None

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        db = get_db()
        docs = db.collection(FirebaseUserService.COLLECTION).stream()
        return [doc.to_dict() for doc in docs]


# ──────────────────────────────────────────────────────────────────────────────
# Analyses Collection
# ──────────────────────────────────────────────────────────────────────────────

class FirebaseAnalysisService:
    """CRUD operations for the 'analyses' collection."""

    COLLECTION = 'analyses'

    @staticmethod
    def create_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
        db = get_db()
        now = datetime.now(timezone.utc).isoformat()

        # Auto-increment ID
        counter_ref = db.collection('counters').document('analyses')
        counter = counter_ref.get()
        new_id = (counter.to_dict().get('next_id', 1)) if counter.exists else 1
        counter_ref.set({'next_id': new_id + 1})

        analysis_data = {
            'id': new_id,
            'user_id': data.get('user_id'),
            'article_title': data.get('article_title', 'Untitled'),
            'article_text': data.get('article_text', ''),
            'article_url': data.get('article_url'),
            'fake_news_score': data.get('fake_news_score', 0.0),
            'fake_news_label': data.get('fake_news_label', 'UNKNOWN'),
            'bias_score': data.get('bias_score', 0.0),
            'bias_label': data.get('bias_label', 'CENTER'),
            'sentiment_score': data.get('sentiment_score', 0.0),
            'sentiment_label': data.get('sentiment_label', 'NEUTRAL'),
            'propaganda_score': data.get('propaganda_score', 0.0),
            'propaganda_techniques': data.get('propaganda_techniques', '[]'),
            'credibility_score': data.get('credibility_score', 0.0),
            'generated_summary': data.get('generated_summary', ''),
            'gemini_explanation': data.get('gemini_explanation', '{}'),
            'keywords': data.get('keywords', '[]'),
            'created_at': now,
        }

        db.collection(FirebaseAnalysisService.COLLECTION).document(str(new_id)).set(analysis_data)
        logger.info('Created analysis id=%d title=%s', new_id, analysis_data['article_title'][:40])
        return analysis_data

    @staticmethod
    def get_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
        db = get_db()
        doc = db.collection(FirebaseAnalysisService.COLLECTION).document(str(analysis_id)).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_history(user_id: Optional[int] = None, page: int = 1,
                    per_page: int = 20) -> Dict[str, Any]:
        db = get_db()
        query = db.collection(FirebaseAnalysisService.COLLECTION) \
            .order_by('created_at', direction=firestore.Query.DESCENDING)

        if user_id is not None:
            query = query.where('user_id', '==', user_id)

        # Get total count
        all_docs = list(query.stream())
        total = len(all_docs)
        pages = max(1, (total + per_page - 1) // per_page)

        # Paginate
        start = (page - 1) * per_page
        end = start + per_page
        page_docs = all_docs[start:end]

        items = []
        for doc in page_docs:
            d = doc.to_dict()
            # Truncate article text in list view
            if d.get('article_text') and len(d['article_text']) > 300:
                d['article_text'] = d['article_text'][:300] + '...'
            items.append(d)

        return {
            'analyses': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages,
                'has_next': page < pages,
                'has_prev': page > 1,
            },
        }

    @staticmethod
    def delete_by_id(analysis_id: int) -> bool:
        db = get_db()
        doc_ref = db.collection(FirebaseAnalysisService.COLLECTION).document(str(analysis_id))
        doc = doc_ref.get()
        if not doc.exists:
            return False
        doc_ref.delete()
        logger.info('Deleted analysis id=%d', analysis_id)
        return True


# ──────────────────────────────────────────────────────────────────────────────
# Reports Collection
# ──────────────────────────────────────────────────────────────────────────────

class FirebaseReportService:
    """CRUD operations for the 'reports' collection."""

    COLLECTION = 'reports'

    @staticmethod
    def create_report(analysis_id: int, report_path: str) -> Dict[str, Any]:
        db = get_db()
        now = datetime.now(timezone.utc).isoformat()

        counter_ref = db.collection('counters').document('reports')
        counter = counter_ref.get()
        new_id = (counter.to_dict().get('next_id', 1)) if counter.exists else 1
        counter_ref.set({'next_id': new_id + 1})

        report_data = {
            'id': new_id,
            'analysis_id': analysis_id,
            'report_path': report_path,
            'created_at': now,
        }
        db.collection(FirebaseReportService.COLLECTION).document(str(new_id)).set(report_data)
        logger.info('Created report id=%d for analysis=%d', new_id, analysis_id)
        return report_data

    @staticmethod
    def get_by_analysis_id(analysis_id: int) -> Optional[Dict[str, Any]]:
        db = get_db()
        docs = db.collection(FirebaseReportService.COLLECTION) \
            .where('analysis_id', '==', analysis_id).limit(1).stream()
        for doc in docs:
            return doc.to_dict()
        return None

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        db = get_db()
        docs = db.collection(FirebaseReportService.COLLECTION) \
            .order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        return [doc.to_dict() for doc in docs]
