import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const PropagandaChart = ({ techniques = [] }) => {
  const defaultTechniques = [
    { name: 'Emotional Appeal', confidence: 0, evidence: 'No evidence detected' },
    { name: 'Loaded Language', confidence: 0, evidence: 'No evidence detected' },
    { name: 'Name Calling', confidence: 0, evidence: 'No evidence detected' },
    { name: 'False Dilemma', confidence: 0, evidence: 'No evidence detected' },
    { name: 'Appeal to Authority', confidence: 0, evidence: 'No evidence detected' },
    { name: 'Bandwagon', confidence: 0, evidence: 'No evidence detected' },
  ];

  const displayTechniques =
    techniques.length > 0 ? techniques.slice(0, 8) : defaultTechniques;

  const getBarColor = (confidence) => {
    if (confidence >= 0.7) return { bg: 'rgba(239, 68, 68, 0.7)', border: '#ef4444' };
    if (confidence >= 0.4) return { bg: 'rgba(245, 158, 11, 0.7)', border: '#f59e0b' };
    return { bg: 'rgba(99, 102, 241, 0.5)', border: '#6366f1' };
  };

  const colors = displayTechniques.map((t) => getBarColor(t.confidence));

  const data = {
    labels: displayTechniques.map((t) => t.name),
    datasets: [
      {
        label: 'Confidence',
        data: displayTechniques.map((t) =>
          typeof t.confidence === 'number' ? +(t.confidence * 100).toFixed(1) : 0
        ),
        backgroundColor: colors.map((c) => c.bg),
        borderColor: colors.map((c) => c.border),
        borderWidth: 1,
        borderRadius: 6,
        borderSkipped: false,
        barThickness: 22,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1e293b',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12,
        titleFont: { family: "'Inter', sans-serif", weight: 600 },
        bodyFont: { family: "'Inter', sans-serif", size: 12 },
        callbacks: {
          title: (items) => items[0]?.label || '',
          label: (context) => ` Confidence: ${context.parsed.x}%`,
          afterLabel: (context) => {
            const tech = displayTechniques[context.dataIndex];
            if (tech?.evidence && tech.evidence !== 'No evidence detected') {
              return `\n Evidence: ${tech.evidence.substring(0, 80)}...`;
            }
            return '';
          },
        },
      },
    },
    scales: {
      x: {
        min: 0,
        max: 100,
        grid: {
          color: 'rgba(255,255,255,0.04)',
          drawBorder: false,
        },
        ticks: {
          color: '#64748b',
          font: { family: "'Inter', sans-serif", size: 11 },
          callback: (value) => `${value}%`,
        },
      },
      y: {
        grid: { display: false },
        ticks: {
          color: '#94a3b8',
          font: { family: "'Inter', sans-serif", size: 12, weight: 500 },
          padding: 8,
        },
      },
    },
    animation: {
      duration: 1200,
      easing: 'easeOutQuart',
    },
  };

  return (
    <div className="chart-container">
      <div className="chart-title">Propaganda Techniques</div>
      <div style={{ height: Math.max(200, displayTechniques.length * 44) }}>
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};

export default PropagandaChart;
