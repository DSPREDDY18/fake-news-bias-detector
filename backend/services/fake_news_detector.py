"""Fake news detection service.

Uses a hybrid approach:
  1. Attempt transformer-based text-classification pipeline.
  2. Fallback to TF-IDF feature extraction + rule-based heuristic scoring
     derived from well-known linguistic indicators of unreliable news.
"""
from __future__ import annotations

import logging
import math
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Linguistic indicator word lists
# --------------------------------------------------------------------------- #

SENSATIONAL_WORDS: set[str] = {
    'shocking', 'unbelievable', 'incredible', 'breaking', 'exclusive',
    'bombshell', 'stunning', 'explosive', 'outrageous', 'horrifying',
    'devastating', 'unprecedented', 'terrifying', 'mind-blowing',
    'jaw-dropping', 'alarming', 'scandalous', 'massive', 'huge',
    'enormous', 'catastrophic', 'insane', 'crazy', 'unreal',
}

HEDGING_WORDS: set[str] = {
    'allegedly', 'reportedly', 'according to', 'sources say', 'claimed',
    'purportedly', 'it is believed', 'some say', 'apparently', 'seemingly',
    'might', 'could', 'possibly', 'perhaps', 'it appears',
}

SUPERLATIVES: set[str] = {
    'best', 'worst', 'greatest', 'largest', 'smallest',
    'most', 'least', 'highest', 'lowest', 'biggest',
    'fastest', 'strongest', 'deadliest', 'richest', 'poorest',
}

ABSOLUTE_WORDS: set[str] = {
    'always', 'never', 'everyone', 'nobody', 'all',
    'none', 'every', 'completely', 'totally', 'absolutely',
    'definitely', 'certainly', 'undoubtedly', 'without doubt',
    'guaranteed', 'proven', 'impossible', 'perfect',
}

CITATION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r'according to [A-Z]', re.IGNORECASE),
    re.compile(r'(?:said|stated|reported|confirmed) (?:by|that)', re.IGNORECASE),
    re.compile(r'(?:study|research|report|survey) (?:by|from|published)', re.IGNORECASE),
    re.compile(r'(?:university|institute|journal|professor|dr\.) ', re.IGNORECASE),
    re.compile(r'(?:official|spokesperson|representative) (?:said|stated|confirmed)', re.IGNORECASE),
]


class FakeNewsDetector:
    """Detects whether a news article is likely fake or real.

    Uses a transformer model when available, falling back to a robust
    TF-IDF + heuristic scoring system.
    """

    def __init__(self) -> None:
        self._pipeline: Any = None
        self._pipeline_loaded: bool = False
        # Skip heavy model loading in production (Render free tier = 512MB)
        import os
        if os.getenv('FLASK_ENV') != 'production':
            self._load_pipeline()
        else:
            logger.info('FakeNewsDetector: skipping transformer in production, using heuristic fallback.')

    # ------------------------------------------------------------------ #
    # Model loading
    # ------------------------------------------------------------------ #
    def _load_pipeline(self) -> None:
        """Attempt to load a HuggingFace text-classification pipeline."""
        try:
            from transformers import pipeline as hf_pipeline
            self._pipeline = hf_pipeline(
                'text-classification',
                model='distilbert-base-uncased-finetuned-sst-2-english',
                truncation=True,
                max_length=512,
            )
            self._pipeline_loaded = True
            logger.info('FakeNewsDetector: transformer pipeline loaded successfully.')
        except Exception as exc:
            logger.warning('FakeNewsDetector: transformer pipeline unavailable (%s). Using fallback.', exc)
            self._pipeline_loaded = False

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze an article for fake news indicators.

        Args:
            text: The full article text.

        Returns:
            A dict with keys: label, confidence, keywords, features.
        """
        features = self._extract_features(text)
        keywords = self._extract_keywords(text)

        if self._pipeline_loaded:
            try:
                result = self._transformer_analysis(text, features)
                result['keywords'] = keywords
                return result
            except Exception as exc:
                logger.warning('Transformer analysis failed (%s), using fallback.', exc)

        return self._heuristic_analysis(text, features, keywords)

    # ------------------------------------------------------------------ #
    # Feature extraction
    # ------------------------------------------------------------------ #
    def _extract_features(self, text: str) -> Dict[str, float]:
        """Compute linguistic features indicative of (un)reliable news."""
        words = text.split()
        word_count = max(len(words), 1)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_count = max(len(sentences), 1)

        # All-caps ratio
        caps_words = sum(1 for w in words if w.isupper() and len(w) > 1)
        caps_ratio = caps_words / word_count

        # Punctuation densities
        exclamation_density = text.count('!') / sentence_count
        question_density = text.count('?') / sentence_count

        # Quote density (number of quotation mark pairs)
        quote_count = text.count('"') // 2 + text.count('\u201c')
        quote_density = quote_count / sentence_count

        # Sensational words
        lower_text = text.lower()
        lower_words = lower_text.split()
        sensational_count = sum(1 for w in lower_words if w.strip('.,!?;:') in SENSATIONAL_WORDS)
        sensational_ratio = sensational_count / word_count

        # Superlatives
        superlative_count = sum(1 for w in lower_words if w.strip('.,!?;:') in SUPERLATIVES)
        superlative_ratio = superlative_count / word_count

        # Absolute words
        absolute_count = sum(1 for w in lower_words if w.strip('.,!?;:') in ABSOLUTE_WORDS)
        absolute_ratio = absolute_count / word_count

        # Hedging language
        hedging_count = sum(1 for phrase in HEDGING_WORDS if phrase in lower_text)
        hedging_ratio = hedging_count / sentence_count

        # Source citations
        citation_count = sum(
            len(pat.findall(text)) for pat in CITATION_PATTERNS
        )
        citation_ratio = citation_count / sentence_count

        # Average sentence length (readability proxy)
        avg_sentence_length = word_count / sentence_count

        # Average word length
        avg_word_length = sum(len(w) for w in words) / word_count

        # Readability (Flesch-Kincaid approximation)
        syllable_count = sum(self._count_syllables(w) for w in words)
        fk_grade = (
            0.39 * (word_count / sentence_count)
            + 11.8 * (syllable_count / word_count)
            - 15.59
        )

        return {
            'caps_ratio': round(caps_ratio, 4),
            'exclamation_density': round(exclamation_density, 4),
            'question_density': round(question_density, 4),
            'quote_density': round(quote_density, 4),
            'sensational_ratio': round(sensational_ratio, 4),
            'superlative_ratio': round(superlative_ratio, 4),
            'absolute_ratio': round(absolute_ratio, 4),
            'hedging_ratio': round(hedging_ratio, 4),
            'citation_ratio': round(citation_ratio, 4),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(avg_word_length, 2),
            'fk_grade_level': round(fk_grade, 2),
            'word_count': word_count,
            'sentence_count': sentence_count,
        }

    @staticmethod
    def _count_syllables(word: str) -> int:
        """Rough syllable count for English words."""
        word = word.lower().strip('.,!?;:\'"')
        if not word:
            return 1
        count = 0
        vowels = 'aeiouy'
        prev_vowel = False
        for ch in word:
            is_vowel = ch in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        if word.endswith('e') and count > 1:
            count -= 1
        return max(count, 1)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract significant keywords using TF-IDF."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            # Split text into pseudo-documents (paragraphs)
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
            if len(paragraphs) < 2:
                # Split into sentence groups
                sentences = re.split(r'[.!?]+', text)
                paragraphs = [s.strip() for s in sentences if len(s.strip()) > 20]

            if len(paragraphs) < 2:
                paragraphs = [text[:len(text) // 2], text[len(text) // 2:]]

            vectorizer = TfidfVectorizer(
                max_features=20,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
            )
            tfidf_matrix = vectorizer.fit_transform(paragraphs)
            feature_names = vectorizer.get_feature_names_out()

            # Sum TF-IDF scores across documents and pick top keywords
            scores = tfidf_matrix.sum(axis=0).A1
            ranked = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
            return [kw for kw, _ in ranked[:10]]
        except Exception:
            # Brute-force keyword extraction
            lower = text.lower()
            words = re.findall(r'\b[a-z]{4,}\b', lower)
            from collections import Counter
            stop = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'they',
                    'their', 'about', 'would', 'could', 'which', 'there', 'these',
                    'other', 'some', 'than', 'into', 'just', 'also', 'more', 'when'}
            counts = Counter(w for w in words if w not in stop)
            return [w for w, _ in counts.most_common(10)]

    # ------------------------------------------------------------------ #
    # Transformer-based analysis
    # ------------------------------------------------------------------ #
    def _transformer_analysis(self, text: str, features: Dict[str, float]) -> Dict[str, Any]:
        """Run the transformer pipeline and blend with heuristic features."""
        # The SST-2 model labels are POSITIVE/NEGATIVE – we map:
        # POSITIVE → REAL, NEGATIVE → FAKE  (as a proxy)
        truncated = text[:512]
        result = self._pipeline(truncated)[0]
        model_label = result['label']
        model_score = result['score']

        # Heuristic credibility penalty
        heuristic_score = self._compute_heuristic_score(features)

        if model_label == 'POSITIVE':
            # Model says "real" – temper with heuristic
            combined_real = model_score * 0.6 + heuristic_score * 0.4
            if combined_real >= 0.5:
                label = 'REAL'
                confidence = min(combined_real, 1.0)
            else:
                label = 'FAKE'
                confidence = min(1.0 - combined_real, 1.0)
        else:
            combined_fake = model_score * 0.6 + (1 - heuristic_score) * 0.4
            if combined_fake >= 0.5:
                label = 'FAKE'
                confidence = min(combined_fake, 1.0)
            else:
                label = 'REAL'
                confidence = min(1.0 - combined_fake, 1.0)

        return {
            'label': label,
            'confidence': round(confidence, 4),
            'features': features,
            'keywords': [],
        }

    # ------------------------------------------------------------------ #
    # Heuristic (fallback) analysis
    # ------------------------------------------------------------------ #
    def _compute_heuristic_score(self, features: Dict[str, float]) -> float:
        """Compute a 0-1 credibility score from linguistic features.

        Higher = more credible (i.e. more likely REAL).
        """
        penalties = 0.0

        # High caps ratio is sensational
        if features['caps_ratio'] > 0.05:
            penalties += min(features['caps_ratio'] * 3, 0.15)

        # Excessive exclamation marks
        if features['exclamation_density'] > 0.3:
            penalties += min(features['exclamation_density'] * 0.2, 0.10)

        # Sensational language
        if features['sensational_ratio'] > 0.01:
            penalties += min(features['sensational_ratio'] * 8, 0.15)

        # Superlatives / absolutes
        combined_extreme = features['superlative_ratio'] + features['absolute_ratio']
        if combined_extreme > 0.01:
            penalties += min(combined_extreme * 5, 0.15)

        # Lack of citations is suspicious
        if features['citation_ratio'] < 0.1:
            penalties += 0.10
        elif features['citation_ratio'] < 0.2:
            penalties += 0.05

        # Very short or very long sentences
        asl = features['avg_sentence_length']
        if asl < 8 or asl > 35:
            penalties += 0.05

        # Low reading level can indicate clickbait
        if features['fk_grade_level'] < 5:
            penalties += 0.05

        # Hedging without citations can go either way but heavy hedging is suspicious
        if features['hedging_ratio'] > 0.3 and features['citation_ratio'] < 0.1:
            penalties += 0.05

        credibility = max(0.0, 1.0 - penalties)
        return round(credibility, 4)

    def _heuristic_analysis(
        self, text: str, features: Dict[str, float], keywords: List[str]
    ) -> Dict[str, Any]:
        """Pure heuristic-based fake news analysis (no ML model required)."""
        credibility = self._compute_heuristic_score(features)

        if credibility >= 0.70:
            label = 'REAL'
            confidence = credibility
        elif credibility >= 0.45:
            label = 'REAL'
            confidence = credibility * 0.9
        else:
            label = 'FAKE'
            confidence = 1.0 - credibility

        return {
            'label': label,
            'confidence': round(min(confidence, 1.0), 4),
            'keywords': keywords,
            'features': features,
        }
