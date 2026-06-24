import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const SentimentChart = ({ positive = 0, negative = 0, neutral = 0 }) => {
  const total = positive + negative + neutral || 1;

  const getDominant = () => {
    if (positive >= negative && positive >= neutral) return { label: 'Positive', color: '#10b981' };
    if (negative >= positive && negative >= neutral) return { label: 'Negative', color: '#ef4444' };
    return { label: 'Neutral', color: '#64748b' };
  };

  const dominant = getDominant();

  const data = {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [
      {
        data: [positive, negative, neutral],
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(100, 116, 139, 0.6)',
        ],
        borderColor: [
          'rgba(16, 185, 129, 1)',
          'rgba(239, 68, 68, 1)',
          'rgba(100, 116, 139, 1)',
        ],
        borderWidth: 2,
        hoverBorderWidth: 3,
        hoverOffset: 8,
        spacing: 3,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    cutout: '72%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#94a3b8',
          font: {
            family: "'Inter', sans-serif",
            size: 12,
            weight: 500,
          },
          padding: 16,
          usePointStyle: true,
          pointStyleWidth: 10,
        },
      },
      tooltip: {
        backgroundColor: '#1e293b',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12,
        titleFont: { family: "'Inter', sans-serif", weight: 600 },
        bodyFont: { family: "'Inter', sans-serif" },
        callbacks: {
          label: (context) => {
            const value = context.parsed;
            const percentage = ((value / total) * 100).toFixed(1);
            return ` ${context.label}: ${percentage}%`;
          },
        },
      },
    },
    animation: {
      animateRotate: true,
      animateScale: true,
      duration: 1200,
      easing: 'easeOutQuart',
    },
  };

  const centerTextPlugin = {
    id: 'centerText',
    afterDraw: (chart) => {
      const { ctx, width, height } = chart;
      const meta = chart.getDatasetMeta(0);
      if (!meta || !meta.data || meta.data.length === 0) return;

      ctx.save();
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      const centerX = width / 2;
      const centerY = height / 2 - 14;

      ctx.font = "800 24px 'Inter', sans-serif";
      ctx.fillStyle = dominant.color;
      ctx.fillText(`${((Math.max(positive, negative, neutral) / total) * 100).toFixed(0)}%`, centerX, centerY);

      ctx.font = "500 11px 'Inter', sans-serif";
      ctx.fillStyle = '#64748b';
      ctx.fillText(dominant.label, centerX, centerY + 22);

      ctx.restore();
    },
  };

  return (
    <div className="chart-container">
      <div className="chart-title">Sentiment Analysis</div>
      <div style={{ maxWidth: 260, margin: '0 auto' }}>
        <Doughnut data={data} options={options} plugins={[centerTextPlugin]} />
      </div>
    </div>
  );
};

export default SentimentChart;
