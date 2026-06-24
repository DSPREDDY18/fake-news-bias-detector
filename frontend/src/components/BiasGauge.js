import React, { useEffect, useState } from 'react';

const BiasGauge = ({ score = 0, label = '' }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // score: -100 (far left) to 100 (far right), 0 = center
  const clampedScore = Math.max(-100, Math.min(100, score));
  const markerPosition = mounted ? ((clampedScore + 100) / 200) * 100 : 50;

  const getBiasLabel = (s) => {
    if (s <= -60) return 'Far Left';
    if (s <= -30) return 'Left';
    if (s <= -10) return 'Center-Left';
    if (s <= 10) return 'Center';
    if (s <= 30) return 'Center-Right';
    if (s <= 60) return 'Right';
    return 'Far Right';
  };

  const getBiasColor = (s) => {
    if (Math.abs(s) <= 10) return '#10b981';
    if (Math.abs(s) <= 30) return '#06b6d4';
    if (Math.abs(s) <= 60) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="bias-gauge-container">
      <div className="d-flex justify-content-between align-items-center mb-2">
        <h6 style={{ margin: 0, fontSize: 'var(--font-size-lg)', fontWeight: 700 }}>
          Political Bias Spectrum
        </h6>
        <span
          style={{
            color: getBiasColor(clampedScore),
            fontWeight: 700,
            fontSize: 'var(--font-size-sm)',
            background: `rgba(${getBiasColor(clampedScore) === '#10b981' ? '16,185,129' : getBiasColor(clampedScore) === '#06b6d4' ? '6,182,212' : getBiasColor(clampedScore) === '#f59e0b' ? '245,158,11' : '239,68,68'}, 0.15)`,
            padding: '4px 12px',
            borderRadius: 'var(--radius-full)',
          }}
        >
          {label || getBiasLabel(clampedScore)}
        </span>
      </div>

      <div className="bias-gauge-track">
        <div className="bias-gauge-center" />
        <div
          className="bias-gauge-marker"
          style={{ left: `${markerPosition}%` }}
        />
      </div>

      <div className="bias-gauge-labels">
        <span>◀ Far Left</span>
        <span>Center</span>
        <span>Far Right ▶</span>
      </div>

      <div className="text-center mt-3">
        <span style={{ color: 'var(--text-tertiary)', fontSize: 'var(--font-size-xs)' }}>
          Score: {clampedScore > 0 ? '+' : ''}{clampedScore}
        </span>
      </div>
    </div>
  );
};

export default BiasGauge;
