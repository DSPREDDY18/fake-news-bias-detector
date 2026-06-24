"""PDF report generation service using ReportLab.

Generates professional multi-section reports for article analysis results.
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    PageBreak,
)

logger = logging.getLogger(__name__)

# Colour palette
COLOR_PRIMARY = colors.HexColor('#1a237e')      # deep blue
COLOR_SECONDARY = colors.HexColor('#283593')
COLOR_ACCENT = colors.HexColor('#42a5f5')
COLOR_SUCCESS = colors.HexColor('#2e7d32')
COLOR_WARNING = colors.HexColor('#f57f17')
COLOR_DANGER = colors.HexColor('#c62828')
COLOR_LIGHT_BG = colors.HexColor('#f5f5f5')
COLOR_WHITE = colors.white
COLOR_BLACK = colors.black


class ReportGenerator:
    """Generates PDF reports from analysis result dictionaries."""

    def __init__(self, reports_dir: str | None = None) -> None:
        self.reports_dir = reports_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', 'reports'
        )
        os.makedirs(self.reports_dir, exist_ok=True)
        self._styles = getSampleStyleSheet()
        self._register_custom_styles()

    # ------------------------------------------------------------------ #
    # Custom paragraph styles
    # ------------------------------------------------------------------ #
    def _register_custom_styles(self) -> None:
        self._styles.add(ParagraphStyle(
            'ReportTitle',
            parent=self._styles['Title'],
            fontSize=24,
            textColor=COLOR_PRIMARY,
            spaceAfter=6,
            alignment=TA_CENTER,
        ))
        self._styles.add(ParagraphStyle(
            'SectionHeading',
            parent=self._styles['Heading2'],
            fontSize=16,
            textColor=COLOR_PRIMARY,
            spaceBefore=18,
            spaceAfter=8,
            borderWidth=0,
        ))
        self._styles.add(ParagraphStyle(
            'SubHeading',
            parent=self._styles['Heading3'],
            fontSize=13,
            textColor=COLOR_SECONDARY,
            spaceBefore=10,
            spaceAfter=4,
        ))
        self._styles.add(ParagraphStyle(
            'BodyJustified',
            parent=self._styles['BodyText'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
        ))
        self._styles.add(ParagraphStyle(
            'ScoreLarge',
            parent=self._styles['Normal'],
            fontSize=36,
            textColor=COLOR_PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=4,
        ))
        self._styles.add(ParagraphStyle(
            'GradeLabel',
            parent=self._styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=COLOR_SECONDARY,
        ))
        self._styles.add(ParagraphStyle(
            'FooterStyle',
            parent=self._styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ))

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def generate(self, analysis: Dict[str, Any]) -> str:
        """Generate a PDF report and return its file path.

        Args:
            analysis: The full analysis dict (same shape as Analysis.to_dict()).

        Returns:
            Absolute path to the generated PDF file.
        """
        filename = f"report_{analysis.get('id', 'unknown')}_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(self.reports_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        story: List[Any] = []

        # Build sections
        self._add_header(story, analysis)
        self._add_credibility_score(story, analysis)
        self._add_article_summary(story, analysis)
        self._add_fake_news_section(story, analysis)
        self._add_bias_section(story, analysis)
        self._add_sentiment_section(story, analysis)
        self._add_propaganda_section(story, analysis)
        self._add_ai_explanations(story, analysis)
        self._add_fact_checks(story, analysis)
        self._add_footer(story)

        doc.build(story)
        logger.info('Report generated: %s', filepath)
        return filepath

    # ------------------------------------------------------------------ #
    # Section builders
    # ------------------------------------------------------------------ #
    def _add_header(self, story: List[Any], analysis: Dict[str, Any]) -> None:
        story.append(Paragraph('Fake News & Bias Detection Report', self._styles['ReportTitle']))
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width='100%', thickness=2, color=COLOR_PRIMARY))
        story.append(Spacer(1, 8))

        title = analysis.get('article_title', 'Untitled')
        story.append(Paragraph(f'<b>Article:</b> {self._esc(title)}', self._styles['BodyJustified']))

        url = analysis.get('article_url')
        if url:
            story.append(Paragraph(f'<b>URL:</b> {self._esc(url)}', self._styles['BodyJustified']))

        ts = analysis.get('created_at', datetime.now(timezone.utc).isoformat())
        story.append(Paragraph(f'<b>Analyzed on:</b> {ts}', self._styles['BodyJustified']))
        story.append(Spacer(1, 12))

    def _add_credibility_score(self, story: List[Any], analysis: Dict[str, Any]) -> None:
        story.append(Paragraph('Credibility Score', self._styles['SectionHeading']))

        score = analysis.get('credibility_score', 0)
        if isinstance(score, dict):
            score_val = score.get('score', 0)
            grade = score.get('grade', 'N/A')
        else:
            score_val = score
            grade = self._score_to_grade(score_val)

        color = COLOR_SUCCESS if score_val >= 70 else (COLOR_WARNING if score_val >= 50 else COLOR_DANGER)

        score_table_data = [
            [Paragraph(f'<font color="{color.hexval()}">{score_val:.0f}/100</font>', self._styles['ScoreLarge'])],
            [Paragraph(f'Grade: <b>{grade}</b>', self._styles['GradeLabel'])],
        ]
        score_table = Table(score_table_data, colWidths=[3 * inch])
        score_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, COLOR_PRIMARY),
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_LIGHT_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 16))

    def _add_article_summary(self, story: List[Any], analysis: Dict[str, Any]) -> None:
        summary = analysis.get('generated_summary')
        if not summary:
            return
        story.append(Paragraph('Article Summary', self._styles['SectionHeading']))
        story.append(Paragraph(self._esc(summary), self._styles['BodyJustified']))
        story.append(Spacer(1, 12))

    def _add_fake_news_section(self, story: List[Any], analysis: Dict[str, Any]) -> None:
        story.append(Paragraph('Fake News Analysis', self._styles['SectionHeading']))
        fn = analysis.get('fake_news', {})
        label = fn.get('label', 'UNKNOWN')
        confidence = fn.get('confidence', 0)
        score = fn.get('score', confidence)

        label_color = COLOR_SUCCESS if label == 'REAL' else COLOR_DANGER
        data = [
            ['Label', Paragraph(f'<font color="{label_color.hexval()}"><b>{label}</b></font>', self._styles['BodyJustified'])],
            ['Confidence', f'{confidence:.1%}'],
        ]
        self._add_info_table(story, data)

        keywords = analysis.get('keywords', [])
        if keywords:
            kw_str = ', '.join(str(k) for k in keywords[:10])
            story.append(Paragraph(f'<b>Key Topics:</b> {self._esc(kw_str)}', self._styles['BodyJustified']))
        story.append(Spacer(1, 12))

    def _add_bias_section(self, story: List[Any], analysis: Dict[str, Any]) -> None:
        story.append(Paragraph('Bias Analysis', self._styles['SectionHeading']))
        bias = analysis.get('bias', {})
        label = bias.get('label', 'CENTER')
        score = bias.get('score', 0)

        data = [
            ['Detected Bias', f'{label}'],
            ['Bias Score', f'{score:+.2f}  (left=-1 … right=+1)'],
        ]
        self._add_info_table(story, data)

        # Visual bias bar
        self._add_bias_bar(story, score)
        story.append(Spacer(1, 12))

    def _add_sentiment_section(self, story: List[Any], analysis: Dict[str, Any]) -> None:
        story.append(Paragraph('Sentiment Analysis', self._styles['SectionHeading']))
        sent = analysis.get('sentiment', {})
        label = sent.get('label', 'NEUTRAL')
        score = sent.get('score', 0)

        data = [
            ['Sentiment', label],
            ['Score', f'{score:+.2f}'],
        ]
        self._add_info_table(story, data)
        story.append(Spacer(1, 12))

    def _add_propaganda_section(self, story: List[Any], analysis: Dict[str, Any]) -> None:
        story.append(Paragraph('Propaganda Detection', self._styles['SectionHeading']))
        prop = analysis.get('propaganda', {})
        score = prop.get('score', 0)
        techniques = prop.get('techniques', [])

        data = [['Propaganda Score', f'{score:.1%}']]
        self._add_info_table(story, data)

        if techniques:
            story.append(Paragraph('Detected Techniques:', self._styles['SubHeading']))
            for tech in techniques:
                name = tech.get('name', 'Unknown')
                conf = tech.get('confidence', 0)
                evidence = tech.get('evidence', [])
                evidence_str = ', '.join(str(e) for e in evidence[:5])
                story.append(Paragraph(
                    f'• <b>{self._esc(name)}</b> (confidence: {conf:.0%}) — '
                    f'<i>{self._esc(evidence_str)}</i>',
                    self._styles['BodyJustified'],
                ))
        else:
            story.append(Paragraph(
                'No propaganda techniques were detected.',
                self._styles['BodyJustified'],
            ))
        story.append(Spacer(1, 12))

    def _add_ai_explanations(self, story: List[Any], analysis: Dict[str, Any]) -> None:
        gemini = analysis.get('gemini_explanation', {})
        if not gemini:
            return
        if isinstance(gemini, str):
            try:
                gemini = json.loads(gemini)
            except (json.JSONDecodeError, TypeError):
                gemini = {'analysis': gemini}

        story.append(Paragraph('AI-Powered Insights', self._styles['SectionHeading']))

        sections_map = {
            'bias_explanation': 'Bias Explanation',
            'misinformation': 'Misinformation Assessment',
            'overall_assessment': 'Overall Assessment',
        }
        for key, heading in sections_map.items():
            content = gemini.get(key)
            if content:
                story.append(Paragraph(heading, self._styles['SubHeading']))
                story.append(Paragraph(self._esc(str(content)), self._styles['BodyJustified']))
                story.append(Spacer(1, 6))

        story.append(Spacer(1, 12))

    def _add_fact_checks(self, story: List[Any], analysis: Dict[str, Any]) -> None:
        gemini = analysis.get('gemini_explanation', {})
        if isinstance(gemini, str):
            try:
                gemini = json.loads(gemini)
            except (json.JSONDecodeError, TypeError):
                gemini = {}

        fact_checks = gemini.get('fact_checks') if isinstance(gemini, dict) else None
        if not fact_checks:
            return

        story.append(Paragraph('Fact-Check Suggestions', self._styles['SectionHeading']))
        story.append(Paragraph(self._esc(str(fact_checks)), self._styles['BodyJustified']))
        story.append(Spacer(1, 12))

    def _add_footer(self, story: List[Any]) -> None:
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width='100%', thickness=1, color=colors.grey))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f'Generated by Fake News & Bias Detection System — '
            f'{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}',
            self._styles['FooterStyle'],
        ))
        story.append(Paragraph(
            'This report is generated by automated analysis and should be used '
            'as a supplement to, not a replacement for, critical thinking.',
            self._styles['FooterStyle'],
        ))

    # ------------------------------------------------------------------ #
    # Table / visual helpers
    # ------------------------------------------------------------------ #
    def _add_info_table(self, story: List[Any], data: list) -> None:
        """Add a two-column key/value table."""
        table = Table(data, colWidths=[2 * inch, 4.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), COLOR_LIGHT_BG),
            ('TEXTCOLOR', (0, 0), (0, -1), COLOR_PRIMARY),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(table)

    def _add_bias_bar(self, story: List[Any], score: float) -> None:
        """Add a simple visual bias bar: LEFT ◄──●──► RIGHT."""
        position = (score + 1) / 2  # 0 … 1
        left_label = 'LEFT'
        right_label = 'RIGHT'
        marker_pos = int(position * 40)
        bar = '─' * marker_pos + '●' + '─' * (40 - marker_pos)
        story.append(Paragraph(
            f'<font size="8">{left_label} ◄{bar}► {right_label}</font>',
            ParagraphStyle('BiasBar', parent=self._styles['Normal'], alignment=TA_CENTER, fontSize=8),
        ))

    # ------------------------------------------------------------------ #
    # Utilities
    # ------------------------------------------------------------------ #
    @staticmethod
    def _esc(text: str) -> str:
        """Escape XML special characters for ReportLab Paragraphs."""
        return (
            text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
        )

    @staticmethod
    def _score_to_grade(score: float) -> str:
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 65:
            return 'C'
        elif score >= 50:
            return 'D'
        return 'F'
