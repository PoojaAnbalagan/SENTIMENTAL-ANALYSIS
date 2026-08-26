import axios from 'axios';

// In development: VITE_API_BASE_URL is unset → falls back to '' (same origin)
// Vite's dev proxy forwards /api/* → http://localhost:8000 (see vite.config.js)
//
// In production Docker / Kubernetes: VITE_API_BASE_URL is also '' (same origin)
// Nginx reverse-proxies /api/* → http://backend:8000
//
// If you ever need to point at a remote backend, set VITE_API_BASE_URL at build time:
//   VITE_API_BASE_URL=https://api.yourdomain.com npm run build
export const BACKEND_URL = import.meta.env.VITE_API_BASE_URL || '';
const API_BASE = `${BACKEND_URL}/api`;

export const api = {
  getHealth: async () => {
    const res = await axios.get(`${API_BASE}/health`);
    return res.data;
  },

  getMetrics: async () => {
    const res = await axios.get(`${API_BASE}/metrics`);
    return res.data;
  },

  predictSentiment: async (text) => {
    const res = await axios.post(`${API_BASE}/predict`, { text });
    return res.data;
  },

  getReviews: async (filters = {}, page = 1, pageSize = 50, sortBy = 'Newest First') => {
    const params = new URLSearchParams();
    if (filters.dateRange) params.append('dateRange', filters.dateRange);
    if (filters.sentiments?.length) params.append('sentiments', filters.sentiments.join(','));
    if (filters.ratings?.length) params.append('ratings', filters.ratings.join(','));
    if (filters.store && filters.store !== 'All Stores') params.append('store', filters.store);
    if (filters.search) params.append('search', filters.search);
    params.append('sortBy', sortBy);
    params.append('page', page);
    params.append('pageSize', pageSize);

    const res = await axios.get(`${API_BASE}/reviews?${params.toString()}`);
    return res.data;
  },

  getAnalytics: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.dateRange) params.append('dateRange', filters.dateRange);
    if (filters.sentiments?.length) params.append('sentiments', filters.sentiments.join(','));
    if (filters.ratings?.length) params.append('ratings', filters.ratings.join(','));
    if (filters.store && filters.store !== 'All Stores') params.append('store', filters.store);
    if (filters.search) params.append('search', filters.search);

    const res = await axios.get(`${API_BASE}/analytics?${params.toString()}`);
    return res.data;
  },

  getModels: async () => {
    const res = await axios.get(`${API_BASE}/models`);
    return res.data;
  },

  getExportUrl: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.dateRange) params.append('dateRange', filters.dateRange);
    if (filters.sentiments?.length) params.append('sentiments', filters.sentiments.join(','));
    if (filters.ratings?.length) params.append('ratings', filters.ratings.join(','));
    if (filters.store && filters.store !== 'All Stores') params.append('store', filters.store);
    if (filters.search) params.append('search', filters.search);
    return `${API_BASE}/export?${params.toString()}`;
  }
};
