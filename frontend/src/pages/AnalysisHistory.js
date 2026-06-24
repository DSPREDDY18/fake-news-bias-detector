import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AnalysisHistory = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');

  const fetchHistory = async (p = 1) => {
    setLoading(true);
    try {
      const res = await api.analysis.getHistory(p, 15);
      const data = res.data;
      setAnalyses(data.analyses || []);
      setTotalPages(data.pagination?.pages || 1);
      setPage(data.pagination?.page || 1);
    } catch (err) {
      console.error('Failed to load history', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchHistory(); }, []);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this analysis?')) return;
    try {
      await api.analysis.deleteById(id);
      setAnalyses(analyses.filter(a => a.id !== id));
    } catch (err) {
      alert('Failed to delete');
    }
  };

  const getScoreBadge = (score, label) => {
    let color = '#6366f1';
    if (score >= 80) color = '#10b981';
    else if (score >= 60) color = '#06b6d4';
    else if (score >= 40) color = '#f59e0b';
    else color = '#ef4444';
    return (
      <span className="badge rounded-pill px-2 py-1" style={{ background: `${color}22`, color, border: `1px solid ${color}44`, fontSize: '0.75rem' }}>
        {label || score}
      </span>
    );
  };

  const filtered = search
    ? analyses.filter(a => (a.article_title || '').toLowerCase().includes(search.toLowerCase()))
    : analyses;

  return (
    <div className="page-container">
      <div className="container py-4">
        <div className="text-center mb-4 slide-up">
          <h1 className="mb-2">Analysis <span className="gradient-text">History</span></h1>
          <p className="text-secondary">Review your past article analyses</p>
        </div>

        {/* Search */}
        <div className="glass-card p-3 mb-4 fade-in">
          <input type="text" className="form-control dark-input" placeholder="🔍 Search by title..."
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>

        {loading ? (
          <div className="text-center py-5"><div className="loading-spinner" /></div>
        ) : filtered.length === 0 ? (
          <div className="glass-card p-5 text-center fade-in">
            <div style={{ fontSize: '3rem' }} className="mb-3">📭</div>
            <h4>No analyses found</h4>
            <p className="text-secondary">Start by analyzing an article</p>
            <button className="btn btn-primary-gradient" onClick={() => navigate('/analyze')}>
              Analyze Article →
            </button>
          </div>
        ) : (
          <div className="glass-card fade-in" style={{ overflow: 'hidden' }}>
            <div className="table-responsive">
              <table className="table table-dark table-hover mb-0" style={{ background: 'transparent' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-glass)' }}>
                    <th className="text-secondary small">Date</th>
                    <th className="text-secondary small">Title</th>
                    <th className="text-secondary small text-center">Credibility</th>
                    <th className="text-secondary small text-center">Fake News</th>
                    <th className="text-secondary small text-center">Bias</th>
                    <th className="text-secondary small text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(a => (
                    <tr key={a.id} onClick={() => navigate(`/analyze?id=${a.id}`)}
                      style={{ cursor: 'pointer', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td className="small text-secondary">
                        {new Date(a.created_at).toLocaleDateString()}
                      </td>
                      <td className="text-truncate" style={{ maxWidth: 250 }}>
                        {a.article_title || 'Untitled Article'}
                      </td>
                      <td className="text-center">
                        {getScoreBadge(Math.round(a.credibility_score || 0), `${Math.round(a.credibility_score || 0)}/100`)}
                      </td>
                      <td className="text-center">
                        {getScoreBadge(
                          a.fake_news_label === 'REAL' ? 80 : 20,
                          a.fake_news_label || '—'
                        )}
                      </td>
                      <td className="text-center">
                        {getScoreBadge(50, a.bias_label || '—')}
                      </td>
                      <td className="text-center">
                        <button className="btn btn-sm btn-outline-danger" onClick={e => handleDelete(a.id, e)}
                          title="Delete">🗑️</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="d-flex justify-content-center gap-2 mt-4">
            <button className="btn btn-outline-glass btn-sm" disabled={page <= 1} onClick={() => fetchHistory(page - 1)}>
              ← Previous
            </button>
            <span className="btn btn-outline-glass btn-sm disabled">{page} / {totalPages}</span>
            <button className="btn btn-outline-glass btn-sm" disabled={page >= totalPages} onClick={() => fetchHistory(page + 1)}>
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisHistory;
