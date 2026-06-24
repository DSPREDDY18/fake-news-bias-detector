import React, { useState } from 'react';

const ExplanationCard = ({
  title = 'Explanation',
  icon = '💡',
  content = '',
  iconBg = 'feature-icon-indigo',
  defaultExpanded = false,
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded);

  if (!content) return null;

  return (
    <div className="glass-card-static explanation-card animate-fade-in" style={{ marginBottom: '12px' }}>
      <div
        className="explanation-header"
        onClick={() => setExpanded(!expanded)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setExpanded(!expanded)}
      >
        <div className={`explanation-icon ${iconBg}`}>{icon}</div>
        <div className="explanation-title">{title}</div>
        <div className={`explanation-toggle ${expanded ? 'expanded' : ''}`}>
          ▾
        </div>
      </div>
      {expanded && (
        <div className="explanation-body">
          {typeof content === 'string' ? (
            content.split('\n').map((paragraph, idx) => (
              <p key={idx} style={{ marginBottom: idx < content.split('\n').length - 1 ? '0.75rem' : 0 }}>
                {paragraph}
              </p>
            ))
          ) : (
            content
          )}
        </div>
      )}
    </div>
  );
};

const ExplanationCards = ({ explanations = {} }) => {
  const cards = [
    {
      key: 'summary',
      title: 'AI Summary',
      icon: '🧠',
      iconBg: 'feature-icon-indigo',
      content: explanations.summary || explanations.ai_summary || '',
      defaultExpanded: true,
    },
    {
      key: 'bias',
      title: 'Bias Explanation',
      icon: '⚖️',
      iconBg: 'feature-icon-amber',
      content: explanations.bias_explanation || explanations.bias || '',
    },
    {
      key: 'misinformation',
      title: 'Misinformation Indicators',
      icon: '🔍',
      iconBg: 'feature-icon-pink',
      content: explanations.misinformation_indicators || explanations.misinformation || '',
    },
    {
      key: 'factcheck',
      title: 'Fact-Check Suggestions',
      icon: '✅',
      iconBg: 'feature-icon-emerald',
      content: explanations.fact_check_suggestions || explanations.fact_check || '',
    },
    {
      key: 'verification',
      title: 'Verification Tips',
      icon: '🛡️',
      iconBg: 'feature-icon-cyan',
      content: explanations.verification_tips || explanations.verification || '',
    },
  ];

  const hasContent = cards.some((card) => card.content);

  if (!hasContent) return null;

  return (
    <div>
      <h5 style={{ marginBottom: '1rem', fontWeight: 700 }}>
        🤖 AI-Powered Explanations
      </h5>
      {cards
        .filter((card) => card.content)
        .map((card) => (
          <ExplanationCard key={card.key} {...card} />
        ))}
    </div>
  );
};

export { ExplanationCard };
export default ExplanationCards;
