import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Tooltip, Legend } from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';
import api from '../services/api';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Tooltip, Legend);

const AdminDashboard = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, avgCredibility: 0, totalReports: 0 });

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.analysis.getHistory(1, 100);
        const data = res.data.analyses || [];
        setAnalyses(data);
        const avg = data.length > 0
          ? Math.round(data.reduce((s, a) => s + (a.credibility_score || 0), 0) / data.length)
          : 0;
        setStats({ total: res.data.pagination?.total || data.length, avgCredibility: avg, totalReports: 0 });

        try {
          const rr = await api.reports.listReports();
          setStats(s => ({ ...s, totalReports: (rr.data.reports || []).length }));
        } catch {}
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  // Credibility distribution
  const credDist = { A: 0, B: 0, C: 0, D: 0, F: 0 };
  analyses.forEach(a => {
    const s = a.credibility_score || 0;
    if (s >= 90) credDist.A++;
    else if (s >= 80) credDist.B++;
    else if (s >= 60) credDist.C++;
    else if (s >= 40) credDist.D++;
    else credDist.F++;
  });

  // Bias distribution
  const biasDist = { LEFT: 0, 'CENTER-LEFT': 0, CENTER: 0, 'CENTER-RIGHT': 0, RIGHT: 0 };
  analyses.forEach(a => {
    const label = a.bias_label || 'CENTER';
    if (biasDist[label] !== undefined) biasDist[label]++;
    else biasDist.CENTER++;
  });

  // Analyses per day (last 7 entries)
  const dateCounts = {};
  analyses.forEach(a => {
    const d = new Date(a.created_at).toLocaleDateString();
    dateCounts[d] = (dateCounts[d] || 0) + 1;
  });
  const dateLabels = Object.keys(dateCounts).slice(-7);
  const dateValues = dateLabels.map(d => dateCounts[d]);

  const chartOptions = {
    responsive: true,
    plugins: { legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } } },
    scales: {
      x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } },
      y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } }
    }
  };

  const overviewCards = [
    { icon: '📊', label: 'Total Analyses', value: stats.total, color: '#6366f1' },
    { icon: '🎯', label: 'Avg Credibility', value: `${stats.avgCredibility}/100`, color: '#10b981' },
    { icon: '📄', label: 'Reports Generated', value: stats.totalReports, color: '#f59e0b' },
    { icon: '📰', label: 'Recent Analyses', value: analyses.length, color: '#06b6d4' },
  ];

  if (loading) {
    return (
      <div className="page-container">
        <div className="container py-5 text-center"><div className="loading-spinner" /></div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="container py-4">
        <div className="text-center mb-4 slide-up">
          <h1 className="mb-2">Admin <span className="gradient-text">Dashboard</span></h1>
          <p className="text-secondary">System analytics and overview</p>
        </div>

        {/* Overview Cards */}
        <div className="row g-3 mb-4">
          {overviewCards.map((c, i) => (
            <div key={i} className="col-6 col-lg-3">
              <div className="glass-card p-4 hover-lift fade-in" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="d-flex align-items-center gap-3">
                  <div style={{ fontSize: '2rem' }}>{c.icon}</div>
                  <div>
                    <div className="text-secondary small">{c.label}</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, color: c.color }}>{c.value}</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Charts */}
        <div className="row g-3 mb-4">
          <div className="col-lg-8">
            <div className="glass-card p-4 h-100">
              <h5 className="mb-3">📈 Analyses Over Time</h5>
              {dateLabels.length > 0 ? (
                <Line data={{
                  labels: dateLabels,
                  datasets: [{
                    label: 'Analyses',
                    data: dateValues,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99,102,241,0.1)',
                    fill: true,
                    tension: 0.4,
                  }]
                }} options={{ ...chartOptions, plugins: { ...chartOptions.plugins, legend: { display: false } } }} />
              ) : <p className="text-secondary text-center">No data yet</p>}
            </div>
          </div>
          <div className="col-lg-4">
            <div className="glass-card p-4 h-100">
              <h5 className="mb-3">🎯 Bias Distribution</h5>
              <Pie data={{
                labels: Object.keys(biasDist),
                datasets: [{
                  data: Object.values(biasDist),
                  backgroundColor: ['#3b82f6', '#60a5fa', '#94a3b8', '#f87171', '#ef4444'],
                  borderWidth: 0,
                }]
              }} options={{ responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 } } } } }} />
            </div>
          </div>
        </div>

        <div className="row g-3 mb-4">
          <div className="col-lg-6">
            <div className="glass-card p-4 h-100">
              <h5 className="mb-3">📊 Credibility Distribution</h5>
              <Bar data={{
                labels: ['A (90+)', 'B (80-89)', 'C (60-79)', 'D (40-59)', 'F (<40)'],
                datasets: [{
                  label: 'Analyses',
                  data: [credDist.A, credDist.B, credDist.C, credDist.D, credDist.F],
                  backgroundColor: ['#10b981', '#06b6d4', '#f59e0b', '#f97316', '#ef4444'],
                  borderRadius: 8,
                }]
              }} options={chartOptions} />
            </div>
          </div>
          <div className="col-lg-6">
            <div className="glass-card p-4 h-100">
              <h5 className="mb-3">📋 Recent Analyses</h5>
              {analyses.slice(0, 5).length > 0 ? (
                <div className="list-group list-group-flush" style={{ background: 'transparent' }}>
                  {analyses.slice(0, 5).map(a => (
                    <div key={a.id} className="list-group-item d-flex justify-content-between align-items-center"
                      style={{ background: 'transparent', borderColor: 'rgba(255,255,255,0.08)', color: '#f1f5f9' }}>
                      <div>
                        <div className="small">{a.article_title || 'Untitled'}</div>
                        <div className="text-secondary" style={{ fontSize: '0.7rem' }}>
                          {new Date(a.created_at).toLocaleString()}
                        </div>
                      </div>
                      <span className="badge rounded-pill" style={{
                        background: (a.credibility_score || 0) >= 60 ? '#10b98133' : '#ef444433',
                        color: (a.credibility_score || 0) >= 60 ? '#10b981' : '#ef4444',
                      }}>
                        {Math.round(a.credibility_score || 0)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : <p className="text-secondary text-center">No analyses yet</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
