"""Gemini AI service for generating explanations, summaries, and fact-check suggestions.

Uses the Google Generative AI SDK with the gemini-2.0-flash model.
All methods degrade gracefully when the API key is not configured or the
API call fails.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Minimum delay between consecutive Gemini calls (seconds)
_RATE_LIMIT_DELAY: float = 0.5


class GeminiService:
    """Wrapper around the Google Generative AI (Gemini) API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.getenv('GEMINI_API_KEY', '')
        self._model: Any = None
        self._available: bool = False
        self._last_call_time: float = 0.0
        self._initialize()

    def _initialize(self) -> None:
        """Configure the Gemini SDK and instantiate the model."""
        if not self._api_key:
            logger.warning('GeminiService: GEMINI_API_KEY not set. AI features will use fallback responses.')
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel('gemini-2.0-flash')
            self._available = True
            logger.info('GeminiService: initialized with model gemini-2.0-flash.')
        except Exception as exc:
            logger.warning('GeminiService: initialization failed (%s). Using fallback.', exc)
            self._available = False

    # ------------------------------------------------------------------ #
    # Rate limiting helper
    # ------------------------------------------------------------------ #
    def _wait_for_rate_limit(self) -> None:
        """Enforce a minimum delay between API calls."""
        now = time.time()
        elapsed = now - self._last_call_time
        if elapsed < _RATE_LIMIT_DELAY:
            time.sleep(_RATE_LIMIT_DELAY - elapsed)
        self._last_call_time = time.time()

    def _call_model(self, prompt: str) -> str:
        """Send a prompt to Gemini and return the response text.

        Args:
            prompt: The full prompt string.

        Returns:
            The model's text response.

        Raises:
            RuntimeError: If the API is unavailable or the call fails.
        """
        if not self._available or self._model is None:
            raise RuntimeError('Gemini API is not available.')

        self._wait_for_rate_limit()
        response = self._model.generate_content(prompt)
        return response.text

    # ------------------------------------------------------------------ #
    # Public methods
    # ------------------------------------------------------------------ #

    def generate_summary(self, text: str) -> str:
        """Generate a concise summary of the article.

        Args:
            text: The full article text.

        Returns:
            A summary string.
        """
        prompt = (
            "You are an expert news analyst. Provide a concise, objective summary "
            "of the following article in 3-5 sentences. Focus on the key facts, "
            "who is involved, and what happened. Do not add opinion.\n\n"
            f"Article:\n{text[:8000]}"
        )
        try:
            return self._call_model(prompt)
        except Exception as exc:
            logger.warning('generate_summary failed: %s', exc)
            return self._fallback_summary(text)

    def explain_bias(self, text: str, bias_result: Dict[str, Any]) -> str:
        """Generate an explanation of the detected bias.

        Args:
            text: The article text.
            bias_result: The output from BiasDetector.analyze().

        Returns:
            A textual explanation of the bias findings.
        """
        indicators_str = ', '.join(
            ind.get('phrase', str(ind)) for ind in bias_result.get('indicators', [])[:10]
        )
        prompt = (
            "You are a media literacy expert. Analyze the political bias in this article.\n\n"
            f"Detected bias label: {bias_result.get('label', 'CENTER')}\n"
            f"Bias score (left=-1 to right=+1): {bias_result.get('score', 0)}\n"
            f"Key indicators found: {indicators_str}\n\n"
            "Explain in 3-5 sentences:\n"
            "1. Why this article may show this bias direction.\n"
            "2. Specific language choices that contribute to the bias.\n"
            "3. How a reader should interpret this bias.\n\n"
            f"Article excerpt:\n{text[:5000]}"
        )
        try:
            return self._call_model(prompt)
        except Exception as exc:
            logger.warning('explain_bias failed: %s', exc)
            return (
                f"The article shows a {bias_result.get('label', 'CENTER')} bias "
                f"(score: {bias_result.get('score', 0)}). "
                "This assessment is based on vocabulary choices, framing, and "
                "attribution patterns found in the text. Readers are encouraged "
                "to seek multiple sources for a balanced perspective."
            )

    def identify_misinformation(self, text: str) -> str:
        """Identify potential misinformation indicators.

        Args:
            text: The article text.

        Returns:
            A textual analysis of misinformation risk.
        """
        prompt = (
            "You are a fact-checking expert. Analyze this article for potential "
            "misinformation indicators. Look for:\n"
            "1. Unverified claims presented as fact\n"
            "2. Misleading statistics or data\n"
            "3. Out-of-context quotes\n"
            "4. Logical fallacies\n"
            "5. Missing important context\n\n"
            "Provide a concise analysis (4-6 sentences) of misinformation risks.\n\n"
            f"Article:\n{text[:6000]}"
        )
        try:
            return self._call_model(prompt)
        except Exception as exc:
            logger.warning('identify_misinformation failed: %s', exc)
            return (
                "Automated misinformation analysis is currently unavailable. "
                "Readers should verify claims by checking primary sources, "
                "looking for corroborating reports from reputable outlets, "
                "and being cautious of emotional language or unsupported statistics."
            )

    def suggest_fact_checks(self, text: str) -> str:
        """Suggest specific fact-checking actions.

        Args:
            text: The article text.

        Returns:
            Fact-checking suggestions as text.
        """
        prompt = (
            "You are a fact-checking advisor. Based on this article, suggest "
            "5 specific fact-checking actions a reader should take. For each:\n"
            "- Identify the specific claim to verify\n"
            "- Suggest where to check (e.g., official databases, government sites, "
            "reputable news archives)\n\n"
            "Format as a numbered list.\n\n"
            f"Article:\n{text[:6000]}"
        )
        try:
            return self._call_model(prompt)
        except Exception as exc:
            logger.warning('suggest_fact_checks failed: %s', exc)
            return (
                "1. Verify key claims using fact-checking sites like Snopes, "
                "PolitiFact, or FactCheck.org.\n"
                "2. Check the original sources cited in the article.\n"
                "3. Search for corroborating reports from other reputable outlets.\n"
                "4. Look up any statistics mentioned in official databases.\n"
                "5. Verify quotes by searching for the original statements."
            )

    def generate_full_analysis(self, text: str, scores: Dict[str, Any]) -> Dict[str, str]:
        """Generate a comprehensive AI-powered analysis.

        Args:
            text: The article text.
            scores: A dict containing results from all detectors.

        Returns:
            Dict with keys: summary, bias_explanation, misinformation,
            fact_checks, overall_assessment.
        """
        summary = self.generate_summary(text)

        bias_result = scores.get('bias', {})
        bias_explanation = self.explain_bias(text, bias_result)

        misinformation = self.identify_misinformation(text)
        fact_checks = self.suggest_fact_checks(text)

        # Overall assessment
        overall_prompt = (
            "You are a senior media analyst. Based on the following analysis results, "
            "provide a brief overall assessment (3-4 sentences) of this article's "
            "reliability and what readers should know.\n\n"
            f"Credibility Score: {scores.get('credibility', {}).get('score', 'N/A')}/100\n"
            f"Fake News Label: {scores.get('fake_news', {}).get('label', 'N/A')} "
            f"(confidence: {scores.get('fake_news', {}).get('confidence', 'N/A')})\n"
            f"Bias: {scores.get('bias', {}).get('label', 'N/A')}\n"
            f"Sentiment: {scores.get('sentiment', {}).get('label', 'N/A')}\n"
            f"Propaganda Score: {scores.get('propaganda', {}).get('score', 'N/A')}\n\n"
            f"Article excerpt:\n{text[:3000]}"
        )
        try:
            overall = self._call_model(overall_prompt)
        except Exception:
            overall = (
                f"This article received a credibility score of "
                f"{scores.get('credibility', {}).get('score', 'N/A')}/100. "
                "Readers should consider the identified bias and propaganda indicators "
                "when interpreting the content and cross-reference claims with "
                "additional reliable sources."
            )

        return {
            'summary': summary,
            'bias_explanation': bias_explanation,
            'misinformation': misinformation,
            'fact_checks': fact_checks,
            'overall_assessment': overall,
        }

    # ------------------------------------------------------------------ #
    # Fallback helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _fallback_summary(text: str) -> str:
        """Generate a simple extractive summary when Gemini is unavailable."""
        sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if len(s.strip()) > 20]
        if not sentences:
            return 'Summary unavailable. The article text could not be summarized automatically.'
        summary_sentences = sentences[:3]
        return '. '.join(summary_sentences) + '.'
