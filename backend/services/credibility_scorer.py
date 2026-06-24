"""Composite credibility scoring service.

Produces a 0–100 score and letter grade by weighting fake-news,
bias, propaganda, sentiment, and source-quality signals.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)


# Weight configuration
WEIGHTS = {
    'fake_news': 0.40,
    'bias': 0.20,
    'propaganda': 0.20,
    'sentiment': 0.10,
    'source_quality': 0.10,
}


class CredibilityScorer:
    """Calculates a composite credibility score for an article."""

    def calculate(
        self,
        fake_result: Dict[str, Any],
        bias_result: Dict[str, Any],
        sentiment_result: Dict[str, Any],
        propaganda_result: Dict[str, Any],
        text: str,
    ) -> Dict[str, Any]:
        """Compute the overall credibility score.

        Args:
            fake_result: Output from FakeNewsDetector.analyze().
            bias_result: Output from BiasDetector.analyze().
            sentiment_result: Output from SentimentAnalyzer.analyze().
            propaganda_result: Output from PropagandaDetector.analyze().
            text: The original article text (for source-quality analysis).

        Returns:
            Dict with keys: score (0-100), grade (A-F), breakdown (component scores).
        """
        # ---- Fake News component (40%) ----
        # Higher when article is classified as REAL with high confidence
        fn_label = fake_result.get('label', 'UNKNOWN')
        fn_confidence = fake_result.get('confidence', 0.5)
        if fn_label == 'REAL':
            fake_news_component = fn_confidence * 100
        elif fn_label == 'FAKE':
            fake_news_component = (1 - fn_confidence) * 100
        else:
            fake_news_component = 50.0

        # ---- Bias component (20%) ----
        # More neutral = higher credibility
        bias_score = abs(bias_result.get('score', 0.0))  # 0 = neutral, 1 = extreme
        bias_component = (1 - bias_score) * 100

        # ---- Propaganda component (20%) ----
        # Lower propaganda score = higher credibility
        prop_score = propaganda_result.get('score', 0.0)
        propaganda_component = (1 - prop_score) * 100

        # ---- Sentiment component (10%) ----
        # More neutral sentiment = higher credibility
        sent_score = abs(sentiment_result.get('score', 0.0))
        sentiment_component = (1 - sent_score) * 100

        # ---- Source Quality component (10%) ----
        source_component = self._evaluate_source_quality(text)

        # Weighted composite
        weighted_score = (
            fake_news_component * WEIGHTS['fake_news']
            + bias_component * WEIGHTS['bias']
            + propaganda_component * WEIGHTS['propaganda']
            + sentiment_component * WEIGHTS['sentiment']
            + source_component * WEIGHTS['source_quality']
        )

        # Clamp
        weighted_score = max(0.0, min(100.0, weighted_score))
        grade = self._score_to_grade(weighted_score)

        return {
            'score': round(weighted_score, 2),
            'grade': grade,
            'breakdown': {
                'fake_news': {
                    'score': round(fake_news_component, 2),
                    'weight': WEIGHTS['fake_news'],
                    'weighted': round(fake_news_component * WEIGHTS['fake_news'], 2),
                },
                'bias': {
                    'score': round(bias_component, 2),
                    'weight': WEIGHTS['bias'],
                    'weighted': round(bias_component * WEIGHTS['bias'], 2),
                },
                'propaganda': {
                    'score': round(propaganda_component, 2),
                    'weight': WEIGHTS['propaganda'],
                    'weighted': round(propaganda_component * WEIGHTS['propaganda'], 2),
                },
                'sentiment': {
                    'score': round(sentiment_component, 2),
                    'weight': WEIGHTS['sentiment'],
                    'weighted': round(sentiment_component * WEIGHTS['sentiment'], 2),
                },
                'source_quality': {
                    'score': round(source_component, 2),
                    'weight': WEIGHTS['source_quality'],
                    'weighted': round(source_component * WEIGHTS['source_quality'], 2),
                },
            },
        }

    # ------------------------------------------------------------------ #
    # Source quality assessment
    # ------------------------------------------------------------------ #
    @staticmethod
    def _evaluate_source_quality(text: str) -> float:
        """Score from 0-100 based on citation presence, quote usage, etc."""
        score = 50.0  # baseline

        # Direct quotations (indicates sourcing)
        quote_pairs = text.count('"') // 2 + text.count('\u201c')
        if quote_pairs >= 3:
            score += 15
        elif quote_pairs >= 1:
            score += 8

        # Attribution patterns
        attributions = len(re.findall(
            r'\b(?:according to|said|stated|reported by|confirmed by)\b',
            text, re.IGNORECASE,
        ))
        if attributions >= 3:
            score += 15
        elif attributions >= 1:
            score += 8

        # Institutional / expert references
        expert_refs = len(re.findall(
            r'\b(?:university|institute|professor|dr\.|ph\.d|journal|study|research|official)\b',
            text, re.IGNORECASE,
        ))
        if expert_refs >= 3:
            score += 10
        elif expert_refs >= 1:
            score += 5

        # Numeric data (stats indicate factual reporting)
        numbers = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
        if numbers >= 5:
            score += 5

        # Penalty: anonymous or vague sources
        vague = len(re.findall(
            r'\b(?:some people say|many believe|sources say|it is believed|rumor has it)\b',
            text, re.IGNORECASE,
        ))
        score -= vague * 5

        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Map a 0-100 score to a letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 65:
            return 'C'
        elif score >= 50:
            return 'D'
        return 'F'
