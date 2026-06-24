# Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Git

### Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start the backend server
python backend/app.py
```

The backend will be available at `http://localhost:5000`.

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`.

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

---

## Docker Deployment

### Prerequisites
- Docker 20+
- docker-compose 2+

### Quick Start
```bash
# Configure environment
cp .env.example .env
# Edit .env with your settings

# Build and start all services
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Services
| Service | Port | Description |
|---------|------|-------------|
| backend | 5000 | Flask API server |
| frontend | 3000 | React app (nginx) |

### Stopping
```bash
docker-compose down

# Remove volumes too
docker-compose down -v
```

---

## Production Deployment

### Security Checklist
- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS with SSL certificates
- [ ] Set `FLASK_ENV=production`
- [ ] Configure CORS for your domain only
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Use environment-specific configurations

### PostgreSQL Setup
```bash
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/fakenews_db
```

### Gunicorn (Production Server)
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "backend.app:create_app()"
```

### Nginx Reverse Proxy
Use the provided `docker/nginx.conf` as a starting point for your production nginx configuration.

---

## Environment Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | *(empty)* | No* |
| `SECRET_KEY` | Flask session secret | `dev-secret-key` | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | `jwt-secret-key` | Yes |
| `DATABASE_URL` | Database URI | `sqlite:///dev.db` | No |
| `FLASK_ENV` | Environment name | `development` | No |
| `FLASK_DEBUG` | Enable debug mode | `1` | No |

> *Without `GEMINI_API_KEY`, the system will work but Gemini-powered features (summaries, explanations) will return placeholder text.

### Getting a Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API key"
3. Create a new API key
4. Add it to your `.env` file

---

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.12+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for port conflicts
netstat -an | findstr 5000
```

### Frontend won't start
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Model download issues
On first run, HuggingFace models (~500MB-1GB) are downloaded automatically. Ensure:
- Internet connection is available
- Sufficient disk space (2GB+)
- No firewall blocking huggingface.co

### Docker issues
```bash
# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```
