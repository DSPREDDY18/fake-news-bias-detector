import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor — attach JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('factlens_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        localStorage.removeItem('factlens_token');
        localStorage.removeItem('factlens_user');
        // Only redirect if not already on auth pages
        if (
          !window.location.pathname.includes('/login') &&
          !window.location.pathname.includes('/register')
        ) {
          window.location.href = '/login';
        }
      }
      const message =
        error.response.data?.message ||
        error.response.data?.error ||
        'An unexpected error occurred';
      return Promise.reject(new Error(message));
    }
    if (error.request) {
      return Promise.reject(
        new Error('Unable to connect to the server. Please check your connection.')
      );
    }
    return Promise.reject(error);
  }
);

// ── Auth API ──────────────────────────────────────────────────────────────
export const authAPI = {
  login: (email, password) =>
    api.post('/auth/login', { email, password }),

  register: (username, email, password) =>
    api.post('/auth/register', { username, email, password }),

  getProfile: () => api.get('/auth/me'),
};

// ── Analysis API ──────────────────────────────────────────────────────────
export const analysisAPI = {
  analyzeText: (text, title = '') =>
    api.post('/analyze/text', { text, title }),

  analyzeUrl: (url) =>
    api.post('/analyze/url', { url }),

  getHistory: (page = 1, perPage = 10) =>
    api.get('/analysis/history', { params: { page, per_page: perPage } }),

  getById: (id) =>
    api.get(`/analysis/${id}`),

  deleteById: (id) =>
    api.delete(`/analysis/${id}`),
};

// ── Reports API ───────────────────────────────────────────────────────────
export const reportsAPI = {
  getReport: (id) =>
    api.get(`/report/${id}`, { responseType: 'blob' }),

  listReports: () =>
    api.get('/reports'),
};

// ── Admin API ─────────────────────────────────────────────────────────────
export const adminAPI = {
  getDashboard: () =>
    api.get('/admin/dashboard'),

  getStats: () =>
    api.get('/admin/stats'),
};

// Unified API object for convenience
const apiService = {
  auth: authAPI,
  analysis: analysisAPI,
  reports: reportsAPI,
  admin: adminAPI,
};

export default apiService;
