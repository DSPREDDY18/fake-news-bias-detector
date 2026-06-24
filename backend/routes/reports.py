"""Report routes (Firebase Firestore backend).

Blueprint: reports
Prefix:    /api

Endpoints:
    GET /report/<analysis_id>  — generate & download a PDF report
    GET /reports               — list all generated reports
"""
from __future__ import annotations

import logging
import os

from flask import Blueprint, jsonify, send_file, current_app

from backend.services.firebase_service import FirebaseAnalysisService, FirebaseReportService
from backend.services.report_generator import ReportGenerator
from backend.utils.errors import NotFoundError

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__, url_prefix='/api')


def _get_report_generator() -> ReportGenerator:
    """Return a ReportGenerator initialised with the configured reports dir."""
    reports_dir = current_app.config.get(
        'REPORTS_DIR',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reports'),
    )
    return ReportGenerator(reports_dir=reports_dir)


# ------------------------------------------------------------------ #
# GET /api/report/<analysis_id>
# ------------------------------------------------------------------ #
@reports_bp.route('/report/<int:analysis_id>', methods=['GET'])
def generate_report(analysis_id: int):
    """Generate a PDF report for the given analysis and return it as a download.

    Returns:
        200: PDF file download
        404: analysis not found
    """
    analysis = FirebaseAnalysisService.get_by_id(analysis_id)
    if analysis is None:
        raise NotFoundError(f'Analysis with id {analysis_id} not found.')

    generator = _get_report_generator()

    try:
        filepath = generator.generate(analysis)
    except Exception as exc:
        logger.error('Failed to generate report for analysis %d: %s', analysis_id, exc)
        raise NotFoundError('Failed to generate the report. Please try again later.')

    # Record in Firebase
    FirebaseReportService.create_report(
        analysis_id=analysis_id, report_path=filepath,
    )

    return send_file(
        filepath,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'analysis_report_{analysis_id}.pdf',
    )


# ------------------------------------------------------------------ #
# GET /api/reports
# ------------------------------------------------------------------ #
@reports_bp.route('/reports', methods=['GET'])
def list_reports():
    """List all generated reports.

    Returns:
        200: { reports: [...] }
    """
    reports = FirebaseReportService.get_all()
    return jsonify({'reports': reports}), 200
