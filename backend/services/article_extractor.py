"""Article extractor service using newspaper3k.

Extracts article content (title, text, authors, publish date, etc.)
from a given URL.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ArticleExtractor:
    """Extracts article metadata and body text from a URL."""

    def extract(self, url: str) -> Dict[str, Any]:
        """Download and parse an article from the given URL.

        Args:
            url: A publicly accessible HTTP(S) URL pointing to a news article.

        Returns:
            A dict with keys: title, text, authors, publish_date,
            top_image, source_url.

        Raises:
            ValueError: If the URL cannot be fetched or the article is empty.
        """
        try:
            from newspaper import Article
        except ImportError as exc:
            logger.error('newspaper3k is not installed: %s', exc)
            raise ValueError('Article extraction library is not available.') from exc

        try:
            article = Article(url)
            article.download()
            article.parse()
        except Exception as exc:
            logger.warning('Failed to download/parse article at %s: %s', url, exc)
            raise ValueError(
                f'Could not fetch or parse the article at the provided URL: {exc}'
            ) from exc

        text = (article.text or '').strip()
        if not text or len(text) < 50:
            raise ValueError(
                'The extracted article text is too short or empty. '
                'The URL may not point to a readable article.'
            )

        # Attempt NLP for keywords (optional, may fail)
        keywords: List[str] = []
        try:
            article.nlp()
            keywords = list(article.keywords or [])
        except Exception:
            pass

        publish_date: Optional[str] = None
        if article.publish_date:
            try:
                publish_date = article.publish_date.isoformat()
            except Exception:
                publish_date = str(article.publish_date)

        return {
            'title': article.title or 'Untitled',
            'text': text,
            'authors': list(article.authors or []),
            'publish_date': publish_date,
            'top_image': article.top_image or None,
            'source_url': url,
            'keywords': keywords,
        }
