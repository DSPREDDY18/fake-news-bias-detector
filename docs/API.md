# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "is_admin": false,
    "created_at": "2025-01-01T00:00:00"
  },
  "access_token": "eyJ..."
}
```

**Errors:**
- `400` - Validation error (weak password, invalid email)
- `409` - Email or username already exists

---

#### POST /auth/login
Authenticate and receive a JWT token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "is_admin": false
  },
  "access_token": "eyJ..."
}
```

**Errors:**
- `401` - Invalid credentials

---

#### GET /auth/me
Get current authenticated user's profile.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "is_admin": false,
    "created_at": "2025-01-01T00:00:00"
  }
}
```

---

### Analysis

#### POST /analyze/text
Analyze article text for fake news, bias, sentiment, and propaganda.

**Request Body:**
```json
{
  "text": "Full article text goes here...",
  "title": "Optional Article Title"
}
```

**Response (200):**
```json
{
  "id": 1,
  "article_title": "Optional Article Title",
  "article_text": "Full article text...",
  "fake_news": {
    "label": "FAKE",
    "confidence": 0.85,
    "keywords": ["shocking", "unbelievable"],
    "features": {
      "caps_ratio": 0.05,
      "exclamation_density": 0.02
    }
  },
  "bias": {
    "label": "CENTER-RIGHT",
    "score": 0.35,
    "confidence": 0.72,
    "indicators": ["market freedom", "traditional values"]
  },
  "sentiment": {
    "label": "NEGATIVE",
    "score": -0.65,
    "confidence": 0.88,
    "breakdown": {
      "positive": 0.10,
      "negative": 0.75,
      "neutral": 0.15
    }
  },
  "propaganda": {
    "score": 0.45,
    "techniques": [
      {
        "name": "Loaded Language",
        "confidence": 0.8,
        "evidence": ["catastrophic failure", "unprecedented crisis"]
      },
      {
        "name": "Fear Appeal",
        "confidence": 0.6,
        "evidence": ["threaten our way of life"]
      }
    ]
  },
  "credibility": {
    "score": 42,
    "grade": "D",
    "breakdown": {
      "fake_news_component": 34,
      "bias_component": 56,
      "propaganda_component": 55,
      "sentiment_component": 35,
      "source_component": 50
    }
  },
  "gemini_analysis": {
    "summary": "AI-generated article summary...",
    "bias_explanation": "The article shows center-right bias...",
    "misinformation_indicators": ["Claim X is not supported by..."],
    "fact_check_suggestions": ["Verify claim X at..."],
    "verification_tips": ["Cross-reference with..."]
  },
  "created_at": "2025-01-01T00:00:00"
}
```

---

#### POST /analyze/url
Extract and analyze an article from a URL.

**Request Body:**
```json
{
  "url": "https://example.com/article"
}
```

**Response:** Same format as POST /analyze/text, with additional `article_url` field.

**Errors:**
- `400` - Invalid URL format
- `422` - Could not extract article from URL

---

#### GET /analysis/history
Get paginated analysis history.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Items per page |
| `sort` | string | `created_at` | Sort field |
| `order` | string | `desc` | Sort order (asc/desc) |

**Response (200):**
```json
{
  "analyses": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "pages": 3
  }
}
```

---

#### GET /analysis/:id
Get a single analysis by ID.

**Response (200):** Full analysis object (same as analyze response).

**Errors:**
- `404` - Analysis not found

---

#### DELETE /analysis/:id
Delete an analysis.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Analysis deleted successfully"
}
```

---

### Reports

#### GET /report/:analysis_id
Generate and download a PDF report for an analysis.

**Response:** PDF file download.

**Errors:**
- `404` - Analysis not found

---

#### GET /reports
List all generated reports.

**Response (200):**
```json
{
  "reports": [
    {
      "id": 1,
      "analysis_id": 1,
      "report_path": "reports/report_1.pdf",
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

---

## Error Responses

All errors follow this format:
```json
{
  "error": {
    "code": 400,
    "type": "ValidationError",
    "message": "Description of what went wrong"
  }
}
```

### HTTP Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request / Validation Error |
| 401 | Unauthorized |
| 404 | Not Found |
| 409 | Conflict (duplicate) |
| 422 | Unprocessable Entity |
| 500 | Internal Server Error |

---

## Rate Limiting

The Gemini API integration includes built-in rate limiting. If the API is unavailable or rate-limited, the system gracefully falls back to local NLP analysis only.
