# FactLens AI — Fake News Bias Detection System

A production-ready AI-powered system for detecting fake news, political bias, propaganda, and sentiment in news articles. Built with Flask, React, Hugging Face Transformers, and Google Gemini.

---

## Features

### 🔍 Fake News Detection
- ML-powered classification (FAKE vs REAL)
- Confidence scoring with linguistic feature analysis
- Keyword extraction for explainable results

### 📊 Political Bias Analysis
- 5-point spectrum: Far Left ↔ Far Right
- Political vocabulary and framing detection
- Quantitative bias score (-1.0 to +1.0)

### 💬 Sentiment Analysis
- Positive / Negative / Neutral classification
- Transformer-based with TextBlob fallback
- Confidence breakdown by category

### 🎭 Propaganda Detection
- 6 propaganda techniques detected:
  - Loaded Language, Fear Appeal, Name Calling
  - Exaggeration, Emotional Manipulation, Cherry Picking
- Evidence-based detection with matched phrases

### 🤖 Generative AI Analysis (Gemini 2.0)
- Article summarization
- Bias explanation
- Misinformation indicator identification
- Fact-check suggestions
- Verification recommendations

### 📈 Interactive Dashboard
- Credibility meter (0-100 score)
- Bias spectrum gauge
- Sentiment & propaganda charts
- Keyword highlighting
- AI explanation cards
- Analysis history & PDF reports

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, Flask, Flask-RESTful, SQLAlchemy |
| **Frontend** | React 18, Bootstrap 5, Chart.js |
| **AI/NLP** | Hugging Face Transformers, scikit-learn, TextBlob |
| **Generative AI** | Google Gemini 2.0 Flash |
| **Database** | SQLite (dev), supports PostgreSQL |
| **Auth** | JWT (Flask-JWT-Extended) |
| **Reports** | ReportLab (PDF generation) |
| **Deployment** | Docker, docker-compose, nginx |

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Google Gemini API key (optional, for AI explanations)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fake-news-bias-detector
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start backend
python backend/app.py
```
Backend runs at: http://localhost:5000

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```
Frontend runs at: http://localhost:3000

### 4. Docker Setup (Alternative)
```bash
# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Build and run
docker-compose up --build
```

---

## API Reference

See [docs/API.md](docs/API.md) for complete API documentation.

### Quick Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT |
| GET | `/api/auth/me` | Get current user profile |
| POST | `/api/analyze/text` | Analyze article text |
| POST | `/api/analyze/url` | Analyze article from URL |
| GET | `/api/analysis/history` | Get analysis history |
| GET | `/api/analysis/<id>` | Get analysis details |
| DELETE | `/api/analysis/<id>` | Delete analysis |
| GET | `/api/report/<id>` | Download PDF report |

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Optional* |
| `SECRET_KEY` | Flask secret key | Yes |
| `JWT_SECRET_KEY` | JWT signing key | Yes |
| `DATABASE_URL` | Database connection string | No (defaults to SQLite) |

*Without Gemini API key, AI-generated explanations will show placeholder messages.

---

## Testing

```bash
cd backend
python -m pytest tests/ -v --cov=.
```

---

## Project Structure

```
fake-news-bias-detector/
├── backend/
│   ├── app.py              # Flask app factory
│   ├── config.py           # Configuration
│   ├── extensions.py       # Flask extensions
│   ├── models/             # SQLAlchemy models
│   ├── routes/             # API route blueprints
│   ├── services/           # AI/NLP analysis services
│   ├── utils/              # Validators, logging, errors
│   ├── reports/            # Generated PDF reports
│   └── tests/              # Test suite
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # Auth context
│   │   ├── pages/          # Page components
│   │   └── services/       # API service layer
│   └── public/
├── docker/                 # Docker configuration
├── docs/                   # Documentation
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## License

MIT License

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/my-feature`)
5. Open a Pull Request
