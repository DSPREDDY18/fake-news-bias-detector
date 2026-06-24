import React, { useEffect, useState, useRef } from 'react';

const ScoreCard = ({
  title = 'Score',
  score = 0,
  maxScore = 100,
  icon = '📊',
  color = 'indigo',
  suffix = '%',
}) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  const rafRef = useRef(null);

  useEffect(() => {
    const duration = 1200;
    const startTime = performance.now();
    const target = Math.min(score, maxScore);

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(Math.round(eased * target));
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    };

    rafRef.current = requestAnimationFrame(animate);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [score, maxScore]);

  const colorMap = {
    indigo: { text: 'var(--accent-primary)', cardClass: 'score-card-indigo' },
    success: { text: 'var(--accent-success)', cardClass: 'score-card-success' },
    warning: { text: 'var(--accent-warning)', cardClass: 'score-card-warning' },
    danger: { text: 'var(--accent-danger)', cardClass: 'score-card-warning' },
    info: { text: 'var(--accent-info)', cardClass: 'score-card-info' },
  };

  const colorConfig = colorMap[color] || colorMap.indigo;
  const percentage = maxScore > 0 ? (score / maxScore) * 100 : 0;

  return (
    <div className={`glass-card score-card ${colorConfig.cardClass}`}>
      <div className="score-icon">{icon}</div>
      <div className="score-label">{title}</div>
      <div className="score-value" style={{ color: colorConfig.text }}>
        {animatedScore}
        <span style={{ fontSize: 'var(--font-size-lg)' }}>{suffix}</span>
      </div>
      <div
        style={{
          height: 4,
          background: 'rgba(255,255,255,0.06)',
          borderRadius: 'var(--radius-full)',
          marginTop: '0.75rem',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${percentage}%`,
            background: colorConfig.text,
            borderRadius: 'var(--radius-full)',
            transition: 'width 1.2s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: `0 0 8px ${colorConfig.text}`,
          }}
        />
      </div>
    </div>
  );
};

export default ScoreCard;
