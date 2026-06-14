import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const householdApi = {
  sync: (userId: string) => api.post(`/api/household/${userId}/sync`),
  getProfile: (userId: string) => api.get(`/api/household/${userId}`),
};

export const predictionsApi = {
  getForHousehold: (householdId: string) => api.get(`/api/predictions/${householdId}`),
};

export const recipesApi = {
  getForHousehold: (userId: string) => api.get(`/api/recipes/${userId}`),
};

export const pricesApi = {
  getFeed: () => api.get('/api/prices/feed'),
  getAlerts: () => api.get('/api/prices/alerts'),
};

export default api;
