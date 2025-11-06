import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error Logs API
export const errorLogsAPI = {
  getAll: (params = {}) => api.get('/api/errors', { params }),
  getById: (id) => api.get(`/api/errors/${id}`),
  create: (data) => api.post('/api/errors', data),
  update: (id, data) => api.patch(`/api/errors/${id}`, data),
  delete: (id) => api.delete(`/api/errors/${id}`),
};

// Statistics API
export const statsAPI = {
  getSummary: (days = 7) => api.get('/api/stats/summary', { params: { days } }),
  getTimeline: (days = 7) => api.get('/api/stats/timeline', { params: { days } }),
  getTopErrors: (limit = 10, days = 7) => api.get('/api/stats/top-errors', { params: { limit, days } }),
};

// Health check
export const healthCheck = () => api.get('/health');

export default api;

