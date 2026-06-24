"""Political bias detection service.

Combines keyword-based vocabulary matching with linguistic analysis
to detect political leaning in news articles.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Political vocabulary dictionaries
# --------------------------------------------------------------------------- #

LEFT_VOCABULARY: Dict[str, float] = {
    # Social justice / equality
    'systemic racism': 1.0, 'racial justice': 0.9, 'social justice': 0.8,
    'income inequality': 0.8, 'wealth gap': 0.7, 'living wage': 0.7,
    'marginalized': 0.7, 'oppression': 0.8, 'privilege': 0.7,
    'intersectionality': 0.9, 'equity': 0.6, 'inclusivity': 0.6,
    # Environment
    'climate crisis': 0.9, 'climate emergency': 0.9, 'green new deal': 1.0,
    'fossil fuel': 0.5, 'renewable energy': 0.4, 'carbon footprint': 0.5,
    'environmental justice': 0.8, 'sustainability': 0.3,
    # Healthcare / welfare
    'universal healthcare': 0.8, 'single payer': 0.9, 'medicare for all': 1.0,
    'social safety net': 0.6, 'public option': 0.7, 'reproductive rights': 0.8,
    'pro-choice': 0.8, 'affordable housing': 0.5, 'food insecurity': 0.5,
    # Governance
    'progressive': 0.7, 'democratic socialism': 1.0, 'grassroots': 0.5,
    'gun control': 0.7, 'gun reform': 0.7, 'common sense gun laws': 0.7,
    'defund the police': 1.0, 'police reform': 0.6, 'mass incarceration': 0.7,
    'immigrant rights': 0.7, 'undocumented workers': 0.7, 'dreamer': 0.6,
    'workers rights': 0.6, 'labor union': 0.5, 'collective bargaining': 0.5,
    # Framing
    'corporate greed': 0.8, 'big pharma': 0.6, 'wall street': 0.4,
    'the 1%': 0.8, 'billionaire class': 0.9, 'tax the rich': 0.9,
}

RIGHT_VOCABULARY: Dict[str, float] = {
    # Economy / governance
    'free market': 0.7, 'deregulation': 0.7, 'small government': 0.8,
    'fiscal responsibility': 0.6, 'tax cuts': 0.6, 'trickle down': 0.5,
    'job creators': 0.8, 'business friendly': 0.6, 'entitlement reform': 0.7,
    'balanced budget': 0.5, 'national debt': 0.4, 'government overreach': 0.8,
    # Culture / values
    'traditional values': 0.8, 'family values': 0.7, 'religious liberty': 0.8,
    'pro-life': 0.8, 'unborn': 0.7, 'sanctity of life': 0.9,
    'second amendment': 0.7, 'gun rights': 0.8, 'right to bear arms': 0.8,
    'law and order': 0.7, 'tough on crime': 0.7, 'back the blue': 0.9,
    # Immigration / sovereignty
    'illegal alien': 1.0, 'illegal immigrant': 0.8, 'border security': 0.7,
    'build the wall': 1.0, 'open borders': 0.7, 'chain migration': 0.9,
    'national sovereignty': 0.7, 'america first': 1.0,
    # Framing
    'mainstream media': 0.7, 'liberal bias': 0.9, 'radical left': 1.0,
    'socialist agenda': 1.0, 'deep state': 1.0, 'cancel culture': 0.8,
    'woke': 0.9, 'political correctness': 0.7, 'nanny state': 0.8,
    'big government': 0.8, 'elites': 0.5, 'patriot': 0.5,
    'freedom': 0.3, 'liberty': 0.3, 'constitution': 0.3,
}

LOADED_LANGUAGE: Dict[str, str] = {
    # Left-loaded
    'regime': 'left', 'authoritarian': 'left', 'fascist': 'left',
    'white supremacy': 'left', 'xenophobic': 'left', 'disenfranchised': 'left',
    # Right-loaded
    'tyranny': 'right', 'radical': 'right', 'extremist': 'right',
    'indoctrination': 'right', 'propaganda': 'right', 'mob': 'right',
}


class BiasDetector:
    """Detects political bias in news articles via vocabulary and framing analysis."""

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze a text for political bias.

        Args:
            text: The full article text.

        Returns:
            A dict with keys: label, score (-1.0 left … +1.0 right),
            confidence, indicators.
        """
        lower_text = text.lower()

        left_score, left_matches = self._score_vocabulary(lower_text, LEFT_VOCABULARY)
        right_score, right_matches = self._score_vocabulary(lower_text, RIGHT_VOCABULARY)
        loaded_indicators = self._detect_loaded_language(lower_text)
        framing_score, framing_indicators = self._analyze_framing(text)

        # Combine scores: positive = right, negative = left
        raw_diff = right_score - left_score
        # Normalise to -1 … 1
        total = left_score + right_score
        if total > 0:
            normalised = raw_diff / total
        else:
            normalised = 0.0

        # Incorporate framing
        combined = normalised * 0.7 + framing_score * 0.3
        combined = max(-1.0, min(1.0, combined))

        label = self._score_to_label(combined)
        confidence = self._compute_confidence(left_score, right_score, left_matches, right_matches)

        indicators: List[Dict[str, Any]] = []
        for phrase in left_matches:
            indicators.append({'phrase': phrase, 'leaning': 'LEFT', 'weight': LEFT_VOCABULARY.get(phrase, 0.5)})
        for phrase in right_matches:
            indicators.append({'phrase': phrase, 'leaning': 'RIGHT', 'weight': RIGHT_VOCABULARY.get(phrase, 0.5)})
        indicators.extend(loaded_indicators)
        indicators.extend(framing_indicators)

        return {
            'label': label,
            'score': round(combined, 4),
            'confidence': round(confidence, 4),
            'indicators': indicators,
        }

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _score_vocabulary(text: str, vocab: Dict[str, float]) -> tuple[float, List[str]]:
        """Sum weighted matches of vocabulary phrases in the text."""
        score = 0.0
        matches: List[str] = []
        for phrase, weight in vocab.items():
            count = text.count(phrase)
            if count > 0:
                score += weight * count
                matches.append(phrase)
        return score, matches

    @staticmethod
    def _detect_loaded_language(text: str) -> List[Dict[str, Any]]:
        """Detect emotionally loaded political language."""
        indicators: List[Dict[str, Any]] = []
        for phrase, direction in LOADED_LANGUAGE.items():
            if phrase in text:
                indicators.append({
                    'phrase': phrase,
                    'type': 'loaded_language',
                    'leaning': direction.upper(),
                })
        return indicators

    @staticmethod
    def _analyze_framing(text: str) -> tuple[float, List[Dict[str, Any]]]:
        """Analyze sentence framing for bias indicators.

        Returns a score (-1 left … +1 right) and a list of framing indicators.
        """
        indicators: List[Dict[str, Any]] = []
        score = 0.0

        # Passive voice about government action (can indicate either direction)
        passive_gov = len(re.findall(
            r'\b(?:was|were|been|being)\s+\w+ed\b.*?\b(?:government|administration|policy)\b',
            text, re.IGNORECASE,
        ))

        # Attribution analysis
        expert_attr = len(re.findall(r'(?:experts?|scientists?|researchers?)\s+(?:say|argue|warn|believe)', text, re.IGNORECASE))
        critic_attr = len(re.findall(r'(?:critics?|opponents?|skeptics?)\s+(?:say|argue|warn|claim)', text, re.IGNORECASE))

        if expert_attr > critic_attr:
            score -= 0.1 * (expert_attr - critic_attr)
            indicators.append({'type': 'framing', 'detail': 'Heavy reliance on expert attribution', 'leaning': 'LEFT'})
        elif critic_attr > expert_attr:
            score += 0.1 * (critic_attr - expert_attr)
            indicators.append({'type': 'framing', 'detail': 'Heavy reliance on critic attribution', 'leaning': 'RIGHT'})

        # Emotional amplifiers
        fear_phrases = len(re.findall(r'\b(?:threatens?|endangers?|destroys?|ruins?)\b', text, re.IGNORECASE))
        if fear_phrases > 3:
            indicators.append({'type': 'framing', 'detail': 'Elevated fear/threat framing', 'leaning': 'NEUTRAL'})

        score = max(-1.0, min(1.0, score))
        return score, indicators

    @staticmethod
    def _score_to_label(score: float) -> str:
        """Map a -1…+1 score to a human-readable bias label."""
        if score <= -0.6:
            return 'LEFT'
        elif score <= -0.2:
            return 'CENTER-LEFT'
        elif score <= 0.2:
            return 'CENTER'
        elif score <= 0.6:
            return 'CENTER-RIGHT'
        else:
            return 'RIGHT'

    @staticmethod
    def _compute_confidence(
        left_score: float, right_score: float,
        left_matches: List[str], right_matches: List[str],
    ) -> float:
        """Estimate confidence based on evidence volume."""
        total_matches = len(left_matches) + len(right_matches)
        if total_matches == 0:
            return 0.3  # low confidence when no indicators found
        # More evidence → higher confidence, capped at 0.95
        evidence_factor = min(total_matches / 15, 1.0)
        return 0.3 + 0.65 * evidence_factor
