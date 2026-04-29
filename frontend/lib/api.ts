import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const authAPI = {
  register: (data: { email: string; password: string; name: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// Decks
export const decksAPI = {
  getAll: () => api.get('/decks'),
  getOne: (id: number) => api.get(`/decks/${id}`),
  create: (data: { name: string; description?: string }) =>
    api.post('/decks', data),
  update: (id: number, data: { name?: string; description?: string }) =>
    api.put(`/decks/${id}`, data),
  delete: (id: number) => api.delete(`/decks/${id}`),
};

// Cards
export const cardsAPI = {
  getAll: (deckId: number) => api.get(`/decks/${deckId}/cards`),
  create: (deckId: number, data: { front: string; back: string }) =>
    api.post(`/decks/${deckId}/cards`, data),
  update: (cardId: number, data: { front: string; back: string }) =>
    api.put(`/cards/${cardId}`, data),
  delete: (cardId: number) => api.delete(`/cards/${cardId}`),
};

// Study
export const studyAPI = {
  getNext: (deckId: number) => api.get(`/study/${deckId}/next`),
  review: (cardId: number, rating: string) =>
    api.post(`/study/review?card_id=${cardId}`, { rating }),
};

// Stats
export const statsAPI = {
  getDashboard: () => api.get('/stats/dashboard'),
};

export default api;
