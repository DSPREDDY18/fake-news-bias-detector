"""Propaganda detection service.

Rule-based detection of six propaganda techniques using keyword/pattern
dictionaries and contextual matching.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Technique definitions: each maps to keyword/phrase lists
# --------------------------------------------------------------------------- #

LOADED_LANGUAGE_TERMS: list[str] = [
    # Emotionally charged words
    'outrageous', 'disgraceful', 'horrific', 'atrocious', 'despicable',
    'vile', 'abhorrent', 'grotesque', 'monstrous', 'reprehensible',
    'appalling', 'sickening', 'shameful', 'deplorable', 'repulsive',
    'wicked', 'evil', 'heroic', 'patriotic', 'glorious',
    'treasonous', 'traitorous', 'corrupt', 'crooked', 'rigged',
    'stolen', 'tyrannical', 'oppressive', 'barbaric', 'savage',
    'heartwarming', 'inspirational', 'courageous', 'brilliant',
    'devastating', 'catastrophic', 'apocalyptic', 'miraculous',
]

FEAR_APPEAL_TERMS: list[str] = [
    'threat', 'danger', 'dangerous', 'crisis', 'emergency',
    'catastrophe', 'disaster', 'collapse', 'destruction', 'annihilation',
    'invasion', 'attack', 'war', 'terror', 'terrorism',
    'death', 'deadly', 'fatal', 'lethal', 'kill',
    'survive', 'survival', 'doom', 'doomsday', 'apocalypse',
    'extinction', 'pandemic', 'plague', 'epidemic', 'contagion',
    'if we don\'t act', 'time is running out', 'point of no return',
    'before it\'s too late', 'lives at stake', 'blood on their hands',
    'existential threat', 'national security threat',
]

NAME_CALLING_TERMS: list[str] = [
    'liar', 'liars', 'crook', 'crooks', 'thug', 'thugs',
    'idiot', 'idiots', 'fool', 'fools', 'moron', 'morons',
    'traitor', 'traitors', 'coward', 'cowards', 'puppet', 'puppets',
    'extremist', 'extremists', 'radical', 'radicals', 'fanatic', 'fanatics',
    'fascist', 'fascists', 'communist', 'communists', 'socialist', 'socialists',
    'snowflake', 'snowflakes', 'elitist', 'elitists', 'globalist', 'globalists',
    'warmonger', 'warmongers', 'demagogue', 'demagogues', 'dictator',
    'hack', 'shill', 'stooge', 'lackey',
]

EXAGGERATION_PATTERNS: list[str] = [
    # Superlatives and absolutes
    'the worst', 'the best', 'the greatest', 'the most',
    'the biggest', 'the largest', 'the smallest',
    'never before', 'in all of history', 'of all time',
    'everyone knows', 'nobody believes', 'always', 'never',
    'completely', 'totally', 'absolutely', 'entirely',
    'without exception', 'without question', 'undeniably',
    'literally', 'unprecedented', 'unimaginable',
    'millions and millions', 'billions', 'countless',
    'infinite', 'enormous', 'massive', 'astronomical',
]

EMOTIONAL_MANIPULATION_TERMS: list[str] = [
    # Sympathy triggers
    'innocent children', 'helpless', 'vulnerable', 'defenseless',
    'suffering', 'victims', 'orphans', 'elderly', 'widows',
    'heartbreaking', 'tragic', 'tears', 'crying', 'sobbing',
    'prayers', 'thoughts and prayers',
    # Outrage triggers
    'taxpayer money', 'hard-working americans', 'your tax dollars',
    'our children', 'our families', 'our future', 'our way of life',
    'wake up', 'open your eyes', 'they don\'t want you to know',
    'the truth they\'re hiding', 'fight back', 'stand up',
    'enough is enough', 'silent majority', 'real americans',
]

CHERRY_PICKING_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r'\bone study\b', re.IGNORECASE),
    re.compile(r'\bsome experts\b', re.IGNORECASE),
    re.compile(r'\ba? ?few (?:people|reports?|sources?)\b', re.IGNORECASE),
    re.compile(r'\bfor example\b.*?\bwhile ignoring\b', re.IGNORECASE),
    re.compile(r'\bconveniently (?:ignor|overlook|omit|forget)', re.IGNORECASE),
    re.compile(r'\bfail(?:s|ed)? to mention\b', re.IGNORECASE),
    re.compile(r'\bselectively\b', re.IGNORECASE),
    re.compile(r'\bcherry[- ]?pick', re.IGNORECASE),
    re.compile(r'\bhand[- ]?picked\b', re.IGNORECASE),
    re.compile(r'\bonly (?:shows?|presents?|mentions?|cites?)\b', re.IGNORECASE),
    re.compile(r'\bwhat they (?:don\'t|won\'t) tell you\b', re.IGNORECASE),
]


class PropagandaDetector:
    """Rule-based propaganda technique detection."""

    TECHNIQUES = [
        {
            'name': 'Loaded Language',
            'description': 'Use of emotionally charged words to influence the audience.',
            'terms': LOADED_LANGUAGE_TERMS,
            'patterns': None,
        },
        {
            'name': 'Fear Appeal',
            'description': 'Building support by instilling fear of a threat.',
            'terms': FEAR_APPEAL_TERMS,
            'patterns': None,
        },
        {
            'name': 'Name Calling',
            'description': 'Labeling opponents with derogatory names.',
            'terms': NAME_CALLING_TERMS,
            'patterns': None,
        },
        {
            'name': 'Exaggeration',
            'description': 'Using superlatives, absolutes, and hyperbole.',
            'terms': EXAGGERATION_PATTERNS,
            'patterns': None,
        },
        {
            'name': 'Emotional Manipulation',
            'description': 'Triggering sympathy or outrage to bypass rational analysis.',
            'terms': EMOTIONAL_MANIPULATION_TERMS,
            'patterns': None,
        },
        {
            'name': 'Cherry Picking',
            'description': 'Selectively presenting evidence while ignoring contradictory data.',
            'terms': None,
            'patterns': CHERRY_PICKING_PATTERNS,
        },
    ]

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text for propaganda techniques.

        Args:
            text: The article text.

        Returns:
            Dict with: score (0.0-1.0), techniques (list of detected techniques).
        """
        lower_text = text.lower()
        word_count = max(len(text.split()), 1)

        detected: List[Dict[str, Any]] = []

        for technique in self.TECHNIQUES:
            name = technique['name']
            evidence: List[str] = []

            # Term-based matching
            if technique['terms']:
                for term in technique['terms']:
                    term_lower = term.lower()
                    if term_lower in lower_text:
                        evidence.append(term)

            # Pattern-based matching
            if technique['patterns']:
                for pattern in technique['patterns']:
                    matches = pattern.findall(text)
                    evidence.extend(matches)

            if evidence:
                # Confidence based on amount of evidence relative to text length
                raw_confidence = min(len(evidence) / max(word_count / 100, 1), 1.0)
                confidence = round(0.3 + 0.7 * raw_confidence, 4)

                detected.append({
                    'name': name,
                    'confidence': confidence,
                    'evidence': list(set(evidence))[:10],  # deduplicate, cap at 10
                })

        # Overall propaganda score: weighted by number of techniques and evidence
        if not detected:
            overall_score = 0.0
        else:
            technique_ratio = len(detected) / len(self.TECHNIQUES)
            avg_confidence = sum(t['confidence'] for t in detected) / len(detected)
            overall_score = technique_ratio * 0.6 + avg_confidence * 0.4

        return {
            'score': round(min(overall_score, 1.0), 4),
            'techniques': detected,
        }
