import React, { useState } from 'react';
import api from '../services/api';
import CredibilityMeter from '../components/CredibilityMeter';
import BiasGauge from '../components/BiasGauge';
import SentimentChart from '../components/SentimentChart';
import PropagandaChart from '../components/PropagandaChart';
import KeywordHighlighter from '../components/KeywordHighlighter';
import ExplanationCard from '../components/ExplanationCard';
import ScoreCard from '../components/ScoreCard';

const AnalyzeArticle = () => {
  const [tab, setTab] = useState('text');
  const [text, setText] = useState('');
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [downloading, setDownloading] = useState(false);

  const handleAnalyze = async () => {
    setError('');
    setResult(null);
    if (tab === 'text' && (!text || text.trim().length < 50)) {
      setError('Please enter at least 50 characters of article text.');
      return;
    }
    if (tab === 'url' && !url.trim()) {
      setError('Please enter a valid URL.');
      return;
    }
    setLoading(true);
    try {
      const res = tab === 'text'
        ? await api.analysis.analyzeText(text, title)
        : await api.analysis.analyzeUrl(url);
      setResult(res.data.analysis || res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || err.response?.data?.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!result?.id) return;
    setDownloading(true);
    try {
      const res = await api.reports.getReport(result.id);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `report_${result.id}.pdf`;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch {
      alert('Failed to download report.');
    } finally {
      setDownloading(false);
    }
  };

  const fakeNews = result?.fake_news || result;
  const bias = result?.bias || result;
  const sentiment = result?.sentiment || result;
  const propaganda = result?.propaganda || result;
  const credibility = result?.credibility || result;
  const gemini = result?.gemini_analysis || result?.gemini_explanation || {};

  return (
    <div className="page-container">
      <div className="container py-4">
        <div className="text-center mb-4 slide-up">
          <h1 className="mb-2">Analyze <span className="gradient-text">Article</span></h1>
          <p className="text-secondary">Paste text or enter a URL to detect fake news, bias, and propaganda</p>
        </div>

        {/* Input Section */}
        <div className="glass-card p-4 mb-4 fade-in">
          <div className="d-flex gap-2 mb-3">
            <button className={`btn ${tab === 'text' ? 'btn-primary-gradient' : 'btn-outline-glass'}`}
              onClick={() => setTab('text')}>📝 Paste Text</button>
            <button className={`btn ${tab === 'url' ? 'btn-primary-gradient' : 'btn-outline-glass'}`}
              onClick={() => setTab('url')}>🔗 Enter URL</button>
          </div>

          {tab === 'text' ? (
            <>
              <input type="text" className="form-control dark-input mb-3" placeholder="Article title (optional)"
                value={title} onChange={e => setTitle(e.target.value)} />
              <textarea className="form-control dark-input" rows={8}
                placeholder="Paste the full article text here (minimum 50 characters)..."
                value={text} onChange={e => setText(e.target.value)} />
              <div className="text-end text-secondary small mt-1">{text.length} characters</div>
            </>
          ) : (
            <input type="url" className="form-control dark-input" placeholder="https://example.com/article"
              value={url} onChange={e => setUrl(e.target.value)} />
          )}

          {error && <div className="alert alert-danger mt-3 py-2">{error}</div>}

          <button className="btn btn-primary-gradient btn-lg w-100 mt-3" onClick={handleAnalyze} disabled={loading}>
            {loading ? (
              <><span className="loading-spinner-sm me-2" /> Analyzing...</>
            ) : (
              '🔍 Analyze Article'
            )}
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-5">
            <div className="loading-spinner mb-3" />
            <p className="text-secondary">Running AI analysis... This may take a moment.</p>
            <div className="d-flex justify-content-center gap-3 flex-wrap mt-3">
              {['Detecting fake news...', 'Analyzing bias...', 'Checking propaganda...', 'Generating explanations...'].map((s, i) => (
                <span key={i} className="badge-pill fade-in" style={{ animationDelay: `${i * 0.5}s` }}>{s}</span>
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="fade-in">
            {/* Credibility Score */}
            <div className="glass-card p-4 mb-4 text-center">
              <h3 className="mb-3">Overall <span className="gradient-text">Credibility Score</span></h3>
              <CredibilityMeter score={credibility?.score ?? credibility?.credibility_score ?? 50}
                grade={credibility?.grade} />
            </div>

            {/* Score Cards Row */}
            <div className="row g-3 mb-4">
              <div className="col-6 col-lg-3">
                <ScoreCard title="Fake News" score={Math.round((fakeNews?.confidence ?? fakeNews?.fake_news_score ?? 0) * 100)}
                  maxScore={100} icon="🔍"
                  color={fakeNews?.label === 'FAKE' || fakeNews?.fake_news_label === 'FAKE' ? '#ef4444' : '#10b981'} />
              </div>
              <div className="col-6 col-lg-3">
                <ScoreCard title="Bias" score={Math.round(Math.abs(bias?.score ?? bias?.bias_score ?? 0) * 100)}
                  maxScore={100} icon="⚖️" color="#f59e0b" />
              </div>
              <div className="col-6 col-lg-3">
                <ScoreCard title="Sentiment" score={Math.round(Math.abs(sentiment?.score ?? sentiment?.sentiment_score ?? 0) * 100)}
                  maxScore={100} icon="💬" color="#06b6d4" />
              </div>
              <div className="col-6 col-lg-3">
                <ScoreCard title="Propaganda" score={Math.round((propaganda?.score ?? propaganda?.propaganda_score ?? 0) * 100)}
                  maxScore={100} icon="🎭" color="#8b5cf6" />
              </div>
            </div>

            {/* Bias Gauge */}
            <div className="glass-card p-4 mb-4">
              <h5 className="mb-3">Political Bias Spectrum</h5>
              <BiasGauge score={bias?.score ?? bias?.bias_score ?? 0}
                label={bias?.label ?? bias?.bias_label ?? 'CENTER'} />
            </div>

            {/* Charts Row */}
            <div className="row g-3 mb-4">
              <div className="col-md-6">
                <div className="glass-card p-4 h-100">
                  <h5 className="mb-3">Sentiment Breakdown</h5>
                  <SentimentChart data={sentiment?.breakdown || { positive: 33, negative: 33, neutral: 34 }}
                    label={sentiment?.label ?? sentiment?.sentiment_label ?? 'NEUTRAL'} />
                </div>
              </div>
              <div className="col-md-6">
                <div className="glass-card p-4 h-100">
                  <h5 className="mb-3">Propaganda Techniques</h5>
                  <PropagandaChart techniques={propaganda?.techniques ?? []} />
                </div>
              </div>
            </div>

            {/* Keywords */}
            {(result?.keywords || fakeNews?.keywords) && (
              <div className="glass-card p-4 mb-4">
                <h5 className="mb-3">🔑 Keyword Analysis</h5>
                <KeywordHighlighter
                  text={result?.article_text || text}
                  keywords={(() => {
                    try {
                      const kw = result?.keywords || fakeNews?.keywords || [];
                      return typeof kw === 'string' ? JSON.parse(kw) : kw;
                    } catch { return []; }
                  })()}
                />
              </div>
            )}

            {/* Gemini Explanations */}
            {gemini && typeof gemini === 'object' && Object.keys(gemini).length > 0 && (
              <div className="mb-4">
                <h4 className="mb-3">🤖 AI <span className="gradient-text">Explanations</span></h4>
                <div className="row g-3">
                  {gemini.summary && (
                    <div className="col-md-6">
                      <ExplanationCard icon="📋" title="Article Summary" content={gemini.summary} />
                    </div>
                  )}
                  {gemini.bias_explanation && (
                    <div className="col-md-6">
                      <ExplanationCard icon="⚖️" title="Bias Explanation" content={gemini.bias_explanation} />
                    </div>
                  )}
                  {gemini.misinformation_indicators && (
                    <div className="col-md-6">
                      <ExplanationCard icon="⚠️" title="Misinformation Indicators"
                        content={Array.isArray(gemini.misinformation_indicators) ? gemini.misinformation_indicators.join('\n• ') : gemini.misinformation_indicators} />
                    </div>
                  )}
                  {gemini.fact_check_suggestions && (
                    <div className="col-md-6">
                      <ExplanationCard icon="✅" title="Fact-Check Suggestions"
                        content={Array.isArray(gemini.fact_check_suggestions) ? gemini.fact_check_suggestions.join('\n• ') : gemini.fact_check_suggestions} />
                    </div>
                  )}
                  {gemini.verification_tips && (
                    <div className="col-md-6">
                      <ExplanationCard icon="🔎" title="Verification Tips"
                        content={Array.isArray(gemini.verification_tips) ? gemini.verification_tips.join('\n• ') : gemini.verification_tips} />
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Download Report */}
            <div className="text-center mb-5">
              <button className="btn btn-primary-gradient btn-lg px-5" onClick={handleDownload} disabled={downloading}>
                {downloading ? '⏳ Generating...' : '📄 Download PDF Report'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyzeArticle;
