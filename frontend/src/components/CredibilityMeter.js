import React, { useEffect, useState, useRef } from 'react';

const CredibilityMeter = ({ score = 0, size = 220 }) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  const [mounted, setMounted] = useState(false);
  const rafRef = useRef(null);

  const radius = (size - 24) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.max(0, Math.min(100, score));

  useEffect(() => {
    setMounted(true);
    // Animated counter
    const duration = 1500;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(Math.round(eased * clampedScore));

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    };

    rafRef.current = requestAnimationFrame(animate);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [clampedScore]);

  const getColor = (s) => {
    if (s >= 80) return '#10b981';
    if (s >= 60) return '#06b6d4';
    if (s >= 40) return '#f59e0b';
    if (s >= 20) return '#f97316';
    return '#ef4444';
  };

  const getGrade = (s) => {
    if (s >= 90) return 'A+';
    if (s >= 80) return 'A';
    if (s >= 70) return 'B';
    if (s >= 60) return 'C';
    if (s >= 50) return 'D';
    return 'F';
  };

  const getLabel = (s) => {
    if (s >= 80) return 'Highly Credible';
    if (s >= 60) return 'Mostly Credible';
    if (s >= 40) return 'Questionable';
    if (s >= 20) return 'Low Credibility';
    return 'Not Credible';
  };

  const color = getColor(clampedScore);
  const offset = mounted
    ? circumference - (clampedScore / 100) * circumference
    : circumference;

  return (
    <div className="credibility-meter" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        className="credibility-ring"
        viewBox={`0 0 ${size} ${size}`}
      >
        {/* Background ring */}
        <circle
          className="credibility-ring-bg"
          cx={size / 2}
          cy={size / 2}
          r={radius}
        />
        {/* Glow filter */}
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {/* Progress ring */}
        <circle
          className="credibility-ring-fill"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          filter="url(#glow)"
          style={{ color }}
        />
      </svg>

      <div className="credibility-center">
        <div className="credibility-score" style={{ color }}>
          {animatedScore}
        </div>
        <div className="credibility-grade" style={{ color }}>
          {getGrade(clampedScore)}
        </div>
        <div className="credibility-label">{getLabel(clampedScore)}</div>
      </div>
    </div>
  );
};

export default CredibilityMeter;
