"""Sentiment analysis service.

Attempts to use the HuggingFace transformers sentiment-analysis pipeline
(distilbert-based); falls back to TextBlob when the model is unavailable.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyzes the overall sentiment of a text."""

    def __init__(self) -> None:
        self._pipeline: Any = None
        self._pipeline_loaded: bool = False
        self._load_pipeline()

    def _load_pipeline(self) -> None:
        """Try to load a HuggingFace sentiment-analysis pipeline."""
        try:
            from transformers import pipeline as hf_pipeline
            self._pipeline = hf_pipeline(
                'sentiment-analysis',
                model='distilbert-base-uncased-finetuned-sst-2-english',
                truncation=True,
                max_length=512,
            )
            self._pipeline_loaded = True
            logger.info('SentimentAnalyzer: transformer pipeline loaded.')
        except Exception as exc:
            logger.warning('SentimentAnalyzer: transformer unavailable (%s). Using TextBlob fallback.', exc)
            self._pipeline_loaded = False

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the given text.

        Args:
            text: The article text.

        Returns:
            Dict with keys: label (POSITIVE|NEGATIVE|NEUTRAL),
            score (-1.0 to 1.0), confidence, breakdown.
        """
        if self._pipeline_loaded:
            try:
                return self._transformer_analysis(text)
            except Exception as exc:
                logger.warning('Transformer sentiment failed (%s). Using TextBlob.', exc)

        return self._textblob_analysis(text)

    # ------------------------------------------------------------------ #
    # Transformer path
    # ------------------------------------------------------------------ #
    def _transformer_analysis(self, text: str) -> Dict[str, Any]:
        """Run the HuggingFace pipeline and map its output."""
        # Process in chunks for long text
        chunks = self._chunk_text(text, max_len=512)
        pos_scores: list[float] = []
        neg_scores: list[float] = []

        for chunk in chunks:
            result = self._pipeline(chunk)[0]
            label = result['label']
            score = result['score']
            if label == 'POSITIVE':
                pos_scores.append(score)
                neg_scores.append(1 - score)
            else:
                neg_scores.append(score)
                pos_scores.append(1 - score)

        avg_pos = sum(pos_scores) / len(pos_scores) if pos_scores else 0.5
        avg_neg = sum(neg_scores) / len(neg_scores) if neg_scores else 0.5

        # Map to -1…+1 scale: positive → +1, negative → -1
        sentiment_score = avg_pos - avg_neg
        sentiment_score = max(-1.0, min(1.0, sentiment_score))

        label = self._score_to_label(sentiment_score)
        neutral_pct = max(0.0, 1.0 - abs(sentiment_score)) * 100

        return {
            'label': label,
            'score': round(sentiment_score, 4),
            'confidence': round(max(avg_pos, avg_neg), 4),
            'breakdown': {
                'positive': round(avg_pos * 100, 2),
                'negative': round(avg_neg * 100, 2),
                'neutral': round(neutral_pct, 2),
            },
        }

    # ------------------------------------------------------------------ #
    # TextBlob fallback
    # ------------------------------------------------------------------ #
    def _textblob_analysis(self, text: str) -> Dict[str, Any]:
        """Use TextBlob for sentiment analysis."""
        try:
            from textblob import TextBlob
        except ImportError:
            logger.error('TextBlob is not installed. Returning neutral sentiment.')
            return self._neutral_result()

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity      # -1 … +1
        subjectivity = blob.sentiment.subjectivity  # 0 … 1

        label = self._score_to_label(polarity)

        if polarity > 0:
            pos_pct = (1 + polarity) / 2 * 100
            neg_pct = (1 - polarity) / 2 * 100
        else:
            pos_pct = (1 + polarity) / 2 * 100
            neg_pct = (1 - polarity) / 2 * 100

        neutral_pct = max(0.0, (1 - abs(polarity)) * 100)

        # Confidence: higher subjectivity → higher confidence in non-neutral result
        confidence = 0.5 + 0.5 * subjectivity * abs(polarity)
        if abs(polarity) < 0.1:
            confidence = 0.5  # low confidence for near-neutral

        return {
            'label': label,
            'score': round(polarity, 4),
            'confidence': round(min(confidence, 1.0), 4),
            'breakdown': {
                'positive': round(pos_pct, 2),
                'negative': round(neg_pct, 2),
                'neutral': round(neutral_pct, 2),
            },
        }

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _score_to_label(score: float) -> str:
        if score > 0.1:
            return 'POSITIVE'
        elif score < -0.1:
            return 'NEGATIVE'
        return 'NEUTRAL'

    @staticmethod
    def _chunk_text(text: str, max_len: int = 512) -> list[str]:
        """Split text into chunks of approximately max_len words."""
        words = text.split()
        chunks: list[str] = []
        for i in range(0, len(words), max_len):
            chunk = ' '.join(words[i:i + max_len])
            if chunk.strip():
                chunks.append(chunk)
        return chunks if chunks else [text[:1000]]

    @staticmethod
    def _neutral_result() -> Dict[str, Any]:
        return {
            'label': 'NEUTRAL',
            'score': 0.0,
            'confidence': 0.3,
            'breakdown': {'positive': 33.33, 'negative': 33.33, 'neutral': 33.34},
        }
