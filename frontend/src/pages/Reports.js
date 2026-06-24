import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.reports.listReports();
        setReports(res.data.reports || []);
      } catch (err) {
        console.error('Failed to load reports', err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  const handleDownload = async (analysisId) => {
    try {
      const res = await api.reports.getReport(analysisId);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `report_${analysisId}.pdf`;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch {
      alert('Failed to download report');
    }
  };

  return (
    <div className="page-container">
      <div className="container py-4">
        <div className="text-center mb-4 slide-up">
          <h1 className="mb-2">📄 <span className="gradient-text">Reports</span></h1>
          <p className="text-secondary">Download detailed PDF analysis reports</p>
        </div>

        {loading ? (
          <div className="text-center py-5"><div className="loading-spinner" /></div>
        ) : reports.length === 0 ? (
          <div className="glass-card p-5 text-center fade-in">
            <div style={{ fontSize: '3rem' }} className="mb-3">📋</div>
            <h4>No reports generated yet</h4>
            <p className="text-secondary">Reports are generated when you download from an analysis result.</p>
          </div>
        ) : (
          <div className="row g-3">
            {reports.map((r) => (
              <div key={r.id} className="col-md-6 col-lg-4">
                <div className="glass-card p-4 hover-lift fade-in">
                  <div className="d-flex align-items-start justify-content-between mb-3">
                    <div>
                      <span style={{ fontSize: '2rem' }}>📄</span>
                    </div>
                    <span className="badge-pill small">
                      {new Date(r.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h6 className="mb-1">Report #{r.id}</h6>
                  <p className="text-secondary small mb-3">Analysis #{r.analysis_id}</p>
                  <button className="btn btn-primary-gradient btn-sm w-100"
                    onClick={() => handleDownload(r.analysis_id)}>
                    ⬇️ Download PDF
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;
