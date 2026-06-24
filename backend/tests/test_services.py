"""Tests for analysis service classes."""
from __future__ import annotations

import pytest

from backend.services.fake_news_detector import FakeNewsDetector
from backend.services.bias_detector import BiasDetector
from backend.services.sentiment_analyzer import SentimentAnalyzer
from backend.services.propaganda_detector import PropagandaDetector
from backend.services.credibility_scorer import CredibilityScorer


# --------------------------------------------------------------------------- #
# Sample texts
# --------------------------------------------------------------------------- #

CREDIBLE_ARTICLE = (
    "The Federal Reserve announced on Wednesday that it would raise interest rates "
    "by 0.25 percentage points, bringing the benchmark rate to a range of 5.25% to "
    "5.50%. According to Fed Chair Jerome Powell, the decision was based on persistent "
    "inflationary pressures observed in the latest economic data. The Bureau of Labor "
    "Statistics reported that consumer prices rose 3.2% year-over-year in July. "
    "Economists from Harvard University and the Brookings Institution had widely "
    "anticipated the move. 'This is consistent with our mandate for price stability,' "
    "Powell stated during the press conference. Markets reacted modestly, with the "
    "S&P 500 declining 0.3% in after-hours trading."
)

SENSATIONAL_ARTICLE = (
    "SHOCKING!! You WON'T BELIEVE what the government is HIDING from you!!! "
    "EXPOSED: The most OUTRAGEOUS scandal in ALL of history! EVERYONE is talking "
    "about this INCREDIBLE cover-up! The WORST president EVER has COMPLETELY "
    "DESTROYED our nation! This is the most DEVASTATING revelation of ALL TIME! "
    "MILLIONS of people are FURIOUS! Share this before they DELETE it! The TRUTH "
    "they don't want you to know will BLOW YOUR MIND! WAKE UP America!!!"
)

LEFT_LEANING_ARTICLE = (
    "The progressive coalition pushed for Medicare for All and universal healthcare "
    "as systemic racism continued to plague marginalized communities. Social justice "
    "advocates called for defund the police initiatives while addressing income inequality "
    "and the wealth gap. Climate crisis experts warned of environmental justice concerns "
    "as corporate greed dominated the billionaire class. The Green New Deal proposal "
    "aimed to address both climate emergency and racial justice simultaneously."
)

RIGHT_LEANING_ARTICLE = (
    "Patriots rallied behind the America First agenda, demanding border security and "
    "opposing illegal aliens flooding into the country. The radical left's socialist agenda "
    "threatens traditional values and religious liberty. Gun rights advocates defended the "
    "Second Amendment while calling for law and order. The deep state and mainstream media "
    "continued their liberal bias, pushing cancel culture and woke ideology against "
    "hard-working Americans who support small government and free market principles."
)


# --------------------------------------------------------------------------- #
# FakeNewsDetector tests
# --------------------------------------------------------------------------- #

class TestFakeNewsDetector:
    """Test the FakeNewsDetector service."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.detector = FakeNewsDetector()

    def test_analyze_returns_required_keys(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        assert 'label' in result
        assert 'confidence' in result
        assert 'keywords' in result
        assert 'features' in result

    def test_label_is_valid(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        assert result['label'] in ('REAL', 'FAKE')

    def test_confidence_range(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        assert 0.0 <= result['confidence'] <= 1.0

    def test_credible_article_leans_real(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        # A well-sourced factual article should lean REAL
        assert result['label'] == 'REAL' or result['confidence'] < 0.7

    def test_sensational_article_has_lower_credibility(self) -> None:
        credible = self.detector.analyze(CREDIBLE_ARTICLE)
        sensational = self.detector.analyze(SENSATIONAL_ARTICLE)
        # The sensational article should have higher fake probability
        if sensational['label'] == 'FAKE':
            assert True  # Good – detected as fake
        else:
            # At minimum, confidence should be lower
            assert sensational['confidence'] <= credible['confidence'] + 0.15

    def test_features_extracted(self) -> None:
        result = self.detector.analyze(SENSATIONAL_ARTICLE)
        features = result['features']
        assert 'caps_ratio' in features
        assert features['caps_ratio'] > 0  # SHOCKING, HIDING, etc.
        assert 'exclamation_density' in features
        assert 'sensational_ratio' in features

    def test_keywords_non_empty(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        assert len(result['keywords']) > 0


# --------------------------------------------------------------------------- #
# BiasDetector tests
# --------------------------------------------------------------------------- #

class TestBiasDetector:
    """Test the BiasDetector service."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.detector = BiasDetector()

    def test_analyze_returns_required_keys(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        assert 'label' in result
        assert 'score' in result
        assert 'confidence' in result
        assert 'indicators' in result

    def test_label_is_valid(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        assert result['label'] in ('LEFT', 'CENTER-LEFT', 'CENTER', 'CENTER-RIGHT', 'RIGHT')

    def test_score_range(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        assert -1.0 <= result['score'] <= 1.0

    def test_left_leaning_detected(self) -> None:
        result = self.detector.analyze(LEFT_LEANING_ARTICLE)
        assert result['score'] < 0  # negative = left
        assert result['label'] in ('LEFT', 'CENTER-LEFT')

    def test_right_leaning_detected(self) -> None:
        result = self.detector.analyze(RIGHT_LEANING_ARTICLE)
        assert result['score'] > 0  # positive = right
        assert result['label'] in ('RIGHT', 'CENTER-RIGHT')

    def test_neutral_article(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        # A balanced news article should be near center
        assert abs(result['score']) < 0.6

    def test_indicators_populated_for_biased_text(self) -> None:
        result = self.detector.analyze(LEFT_LEANING_ARTICLE)
        assert len(result['indicators']) > 0


# --------------------------------------------------------------------------- #
# SentimentAnalyzer tests
# --------------------------------------------------------------------------- #

class TestSentimentAnalyzer:
    """Test the SentimentAnalyzer service."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.analyzer = SentimentAnalyzer()

    def test_analyze_returns_required_keys(self) -> None:
        result = self.analyzer.analyze(CREDIBLE_ARTICLE)
        assert 'label' in result
        assert 'score' in result
        assert 'confidence' in result
        assert 'breakdown' in result

    def test_label_is_valid(self) -> None:
        result = self.analyzer.analyze(CREDIBLE_ARTICLE)
        assert result['label'] in ('POSITIVE', 'NEGATIVE', 'NEUTRAL')

    def test_score_range(self) -> None:
        result = self.analyzer.analyze(CREDIBLE_ARTICLE)
        assert -1.0 <= result['score'] <= 1.0

    def test_breakdown_structure(self) -> None:
        result = self.analyzer.analyze(CREDIBLE_ARTICLE)
        breakdown = result['breakdown']
        assert 'positive' in breakdown
        assert 'negative' in breakdown
        assert 'neutral' in breakdown

    def test_negative_sentiment(self) -> None:
        negative_text = (
            "This terrible disaster has caused widespread suffering and devastation. "
            "Thousands of people lost their homes and are struggling to survive. "
            "The awful conditions continue to worsen with no relief in sight. "
            "Authorities have failed miserably to respond to this horrible crisis."
        )
        result = self.analyzer.analyze(negative_text)
        assert result['score'] < 0 or result['label'] == 'NEGATIVE'


# --------------------------------------------------------------------------- #
# PropagandaDetector tests
# --------------------------------------------------------------------------- #

class TestPropagandaDetector:
    """Test the PropagandaDetector service."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.detector = PropagandaDetector()

    def test_analyze_returns_required_keys(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        assert 'score' in result
        assert 'techniques' in result

    def test_score_range(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        assert 0.0 <= result['score'] <= 1.0

    def test_credible_article_low_propaganda(self) -> None:
        result = self.detector.analyze(CREDIBLE_ARTICLE)
        assert result['score'] < 0.5

    def test_sensational_article_higher_propaganda(self) -> None:
        result = self.detector.analyze(SENSATIONAL_ARTICLE)
        assert result['score'] > 0.1  # Should detect at least some techniques

    def test_techniques_have_required_fields(self) -> None:
        result = self.detector.analyze(SENSATIONAL_ARTICLE)
        for tech in result['techniques']:
            assert 'name' in tech
            assert 'confidence' in tech
            assert 'evidence' in tech
            assert isinstance(tech['evidence'], list)

    def test_loaded_language_detected(self) -> None:
        text = (
            "This outrageous and despicable decision is the most appalling act of "
            "corruption ever witnessed. The vile perpetrators should be ashamed of "
            "their reprehensible behaviour. This sickening display is truly shameful."
        )
        result = self.detector.analyze(text)
        technique_names = [t['name'] for t in result['techniques']]
        assert 'Loaded Language' in technique_names


# --------------------------------------------------------------------------- #
# CredibilityScorer tests
# --------------------------------------------------------------------------- #

class TestCredibilityScorer:
    """Test the CredibilityScorer service."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.scorer = CredibilityScorer()

    def _make_results(
        self,
        fn_label='REAL', fn_conf=0.8,
        bias_score=0.0,
        sent_score=0.0,
        prop_score=0.0,
    ) -> tuple:
        fake_result = {'label': fn_label, 'confidence': fn_conf}
        bias_result = {'label': 'CENTER', 'score': bias_score}
        sentiment_result = {'label': 'NEUTRAL', 'score': sent_score}
        propaganda_result = {'score': prop_score, 'techniques': []}
        return fake_result, bias_result, sentiment_result, propaganda_result

    def test_calculate_returns_required_keys(self) -> None:
        fake, bias, sent, prop = self._make_results()
        result = self.scorer.calculate(fake, bias, sent, prop, CREDIBLE_ARTICLE)
        assert 'score' in result
        assert 'grade' in result
        assert 'breakdown' in result

    def test_score_range(self) -> None:
        fake, bias, sent, prop = self._make_results()
        result = self.scorer.calculate(fake, bias, sent, prop, CREDIBLE_ARTICLE)
        assert 0 <= result['score'] <= 100

    def test_grade_valid(self) -> None:
        fake, bias, sent, prop = self._make_results()
        result = self.scorer.calculate(fake, bias, sent, prop, CREDIBLE_ARTICLE)
        assert result['grade'] in ('A', 'B', 'C', 'D', 'F')

    def test_high_credibility_for_good_signals(self) -> None:
        fake, bias, sent, prop = self._make_results(
            fn_label='REAL', fn_conf=0.9, bias_score=0.0, prop_score=0.0,
        )
        result = self.scorer.calculate(fake, bias, sent, prop, CREDIBLE_ARTICLE)
        assert result['score'] >= 70

    def test_low_credibility_for_bad_signals(self) -> None:
        fake, bias, sent, prop = self._make_results(
            fn_label='FAKE', fn_conf=0.9, bias_score=0.8, prop_score=0.8, sent_score=0.9,
        )
        result = self.scorer.calculate(fake, bias, sent, prop, SENSATIONAL_ARTICLE)
        assert result['score'] < 50

    def test_breakdown_components(self) -> None:
        fake, bias, sent, prop = self._make_results()
        result = self.scorer.calculate(fake, bias, sent, prop, CREDIBLE_ARTICLE)
        breakdown = result['breakdown']
        assert 'fake_news' in breakdown
        assert 'bias' in breakdown
        assert 'propaganda' in breakdown
        assert 'sentiment' in breakdown
        assert 'source_quality' in breakdown
