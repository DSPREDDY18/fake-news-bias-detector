import React, { useState } from 'react';

const KeywordHighlighter = ({ text = '', keywords = [] }) => {
  const [activeTooltip, setActiveTooltip] = useState(null);

  if (!text) {
    return (
      <div className="empty-state" style={{ padding: '2rem' }}>
        <div className="empty-state-icon">📝</div>
        <div className="empty-state-text">No text to display</div>
      </div>
    );
  }

  // Build keyword map: { word: { category, reason } }
  const keywordMap = {};
  if (Array.isArray(keywords)) {
    keywords.forEach((kw) => {
      const word = (kw.word || kw.keyword || kw.text || '').toLowerCase();
      if (word) {
        keywordMap[word] = {
          category: kw.category || kw.type || 'fake',
          reason: kw.reason || kw.explanation || `Flagged as ${kw.category || 'suspicious'}`,
        };
      }
    });
  }

  const getCategoryClass = (category) => {
    switch (category?.toLowerCase()) {
      case 'bias':
        return 'keyword-bias';
      case 'propaganda':
        return 'keyword-propaganda';
      case 'fake':
      case 'misinformation':
      default:
        return 'keyword-fake';
    }
  };

  // Simple word-by-word highlighting
  const renderHighlightedText = () => {
    if (Object.keys(keywordMap).length === 0) {
      return <span>{text}</span>;
    }

    const words = text.split(/(\s+)/);
    return words.map((word, index) => {
      const cleanWord = word.toLowerCase().replace(/[^a-z0-9'-]/g, '');
      const match = keywordMap[cleanWord];

      if (match) {
        return (
          <span
            key={index}
            className={getCategoryClass(match.category)}
            onMouseEnter={() => setActiveTooltip(index)}
            onMouseLeave={() => setActiveTooltip(null)}
            style={{ position: 'relative', display: 'inline' }}
          >
            {word}
            {activeTooltip === index && (
              <span className="keyword-tooltip">{match.reason}</span>
            )}
          </span>
        );
      }

      return <span key={index}>{word}</span>;
    });
  };

  const legendItems = [
    { label: 'Misinformation', className: 'keyword-fake' },
    { label: 'Bias', className: 'keyword-bias' },
    { label: 'Propaganda', className: 'keyword-propaganda' },
  ];

  return (
    <div>
      <div
        style={{
          display: 'flex',
          gap: '16px',
          marginBottom: '12px',
          padding: '0 1.5rem',
          flexWrap: 'wrap',
        }}
      >
        {legendItems.map((item) => (
          <span
            key={item.label}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: 'var(--font-size-xs)',
              color: 'var(--text-tertiary)',
            }}
          >
            <span
              className={item.className}
              style={{
                padding: '1px 8px',
                fontSize: 'var(--font-size-xs)',
                display: 'inline-block',
              }}
            >
              Aa
            </span>
            {item.label}
          </span>
        ))}
      </div>
      <div className="keyword-container">{renderHighlightedText()}</div>
    </div>
  );
};

export default KeywordHighlighter;
