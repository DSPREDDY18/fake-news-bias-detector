import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import RegisterForm from '../components/RegisterForm';
import { useAuth } from '../contexts/AuthContext';

const AnimatedCounter = ({ end, duration = 2000, suffix = '' }) => {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const started = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true;
        let start = 0;
        const step = end / (duration / 16);
        const timer = setInterval(() => {
          start += step;
          if (start >= end) { setCount(end); clearInterval(timer); }
          else setCount(Math.floor(start));
        }, 16);
      }
    }, { threshold: 0.3 });
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [end, duration]);

  return <span ref={ref}>{count.toLocaleString()}{suffix}</span>;
};

const Home = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [authMode, setAuthMode] = useState(null); // null | 'login' | 'register'

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('login') === 'true') setAuthMode('login');
    if (params.get('register') === 'true') setAuthMode('register');
  }, []);

  const features = [
    { icon: '🔍', title: 'Fake News Detection', desc: 'AI-powered classification to identify misleading content with confidence scoring and keyword analysis.' },
    { icon: '⚖️', title: 'Bias Analysis', desc: 'Detect political leaning on a 5-point spectrum from Far Left to Far Right with supporting evidence.' },
    { icon: '🎭', title: 'Propaganda Detection', desc: 'Identify 6 propaganda techniques including loaded language, fear appeal, and emotional manipulation.' },
    { icon: '🤖', title: 'AI Explanations', desc: 'Gemini-powered natural language explanations with fact-check suggestions and verification tips.' },
  ];

  const steps = [
    { num: '01', title: 'Submit Article', desc: 'Paste article text or enter a URL for automatic extraction.' },
    { num: '02', title: 'AI Analysis', desc: 'Our models analyze for fake news, bias, sentiment, and propaganda.' },
    { num: '03', title: 'Get Results', desc: 'View credibility scores, charts, explanations, and download PDF reports.' },
  ];

  return (
    <div className="page-container">
      {/* Auth Modal */}
      {authMode && (
        <div className="modal-overlay" onClick={() => setAuthMode(null)}>
          <div className="fade-in" onClick={e => e.stopPropagation()} style={{ position: 'relative', zIndex: 1001 }}>
            {authMode === 'login'
              ? <LoginForm onSwitch={() => setAuthMode('register')} onSuccess={() => setAuthMode(null)} />
              : <RegisterForm onSwitch={() => setAuthMode('login')} onSuccess={() => setAuthMode(null)} />}
          </div>
        </div>
      )}

      {/* Hero Section */}
      <section className="hero-section text-center">
        <div className="hero-bg-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
        <div className="container position-relative">
          <div className="slide-up">
            <span className="badge-pill mb-3">🛡️ AI-Powered News Analysis</span>
            <h1 className="hero-title">
              Detect Fake News with<br />
              <span className="gradient-text">AI-Powered Analysis</span>
            </h1>
            <p className="hero-subtitle mx-auto" style={{ maxWidth: 600 }}>
              Uncover misinformation, political bias, and propaganda in seconds.
              Get credibility scores, AI explanations, and fact-check suggestions.
            </p>
            <div className="d-flex gap-3 justify-content-center mt-4">
              <button className="btn btn-primary-gradient btn-lg px-5" onClick={() => navigate('/analyze')}>
                Analyze Article Now →
              </button>
              {!user && (
                <button className="btn btn-outline-glass btn-lg px-4" onClick={() => setAuthMode('register')}>
                  Get Started Free
                </button>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-5">
        <div className="container">
          <div className="row g-4 text-center">
            {[
              { value: 50000, suffix: '+', label: 'Articles Analyzed' },
              { value: 94, suffix: '%', label: 'Detection Accuracy' },
              { value: 6, suffix: '', label: 'Propaganda Techniques' },
              { value: 5, suffix: '', label: 'Analysis Dimensions' },
            ].map((stat, i) => (
              <div key={i} className="col-6 col-md-3">
                <div className="glass-card p-4 h-100 text-center hover-lift">
                  <h2 className="gradient-text mb-1" style={{ fontSize: '2.5rem', fontWeight: 800 }}>
                    <AnimatedCounter end={stat.value} suffix={stat.suffix} />
                  </h2>
                  <p className="text-secondary mb-0 small">{stat.label}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-5">
        <div className="container">
          <h2 className="text-center mb-2">Comprehensive <span className="gradient-text">Analysis Suite</span></h2>
          <p className="text-secondary text-center mb-5">Everything you need to evaluate news credibility</p>
          <div className="row g-4">
            {features.map((f, i) => (
              <div key={i} className="col-md-6 col-lg-3">
                <div className="glass-card p-4 h-100 hover-lift" style={{ animationDelay: `${i * 0.1}s` }}>
                  <div style={{ fontSize: '2.5rem' }} className="mb-3">{f.icon}</div>
                  <h5 className="mb-2">{f.title}</h5>
                  <p className="text-secondary small mb-0">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-5">
        <div className="container">
          <h2 className="text-center mb-2">How It <span className="gradient-text">Works</span></h2>
          <p className="text-secondary text-center mb-5">Three simple steps to verify any news article</p>
          <div className="row g-4">
            {steps.map((s, i) => (
              <div key={i} className="col-md-4">
                <div className="glass-card p-4 h-100 text-center hover-lift">
                  <div className="gradient-text" style={{ fontSize: '3rem', fontWeight: 800, opacity: 0.6 }}>{s.num}</div>
                  <h5 className="mb-2">{s.title}</h5>
                  <p className="text-secondary small mb-0">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-5 mb-5">
        <div className="container">
          <div className="glass-card p-5 text-center" style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15))' }}>
            <h2 className="mb-3">Ready to <span className="gradient-text">Fight Misinformation</span>?</h2>
            <p className="text-secondary mb-4">Start analyzing articles now — no account required.</p>
            <button className="btn btn-primary-gradient btn-lg px-5" onClick={() => navigate('/analyze')}>
              Start Analyzing →
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
