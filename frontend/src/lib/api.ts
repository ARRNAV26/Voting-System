import axios from 'axios';
import { 
  User, 
  Suggestion, 
  AuthResponse, 
  LoginForm, 
  RegisterForm, 
  SuggestionForm, 
  VoteForm,
  CategoryStats 
} from '../types';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: LoginForm): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },

  register: async (userData: RegisterForm): Promise<User> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Suggestions API
export const suggestionsAPI = {
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    category?: string;
    status?: string;
  }): Promise<Suggestion[]> => {
    const response = await api.get('/suggestions', { params });
    return response.data;
  },

  getTop: async (limit: number = 10): Promise<Suggestion[]> => {
    const response = await api.get('/suggestions/top', { params: { limit } });
    return response.data;
  },

  getById: async (id: number): Promise<Suggestion> => {
    const response = await api.get(`/suggestions/${id}`);
    return response.data;
  },

  create: async (suggestion: SuggestionForm): Promise<Suggestion> => {
    const response = await api.post('/suggestions', suggestion);
    return response.data;
  },

  update: async (id: number, suggestion: Partial<SuggestionForm>): Promise<Suggestion> => {
    const response = await api.put(`/suggestions/${id}`, suggestion);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/suggestions/${id}`);
  },

  getCategories: async (): Promise<CategoryStats[]> => {
    const response = await api.get('/suggestions/categories');
    return response.data;
  },
};

// Votes API
export const votesAPI = {
  create: async (vote: VoteForm): Promise<any> => {
    const response = await api.post('/votes', vote);
    return response.data;
  },

  remove: async (suggestionId: number): Promise<any> => {
    const response = await api.delete(`/votes/${suggestionId}`);
    return response.data;
  },

  getVoteInfo: async (suggestionId: number): Promise<any> => {
    const response = await api.get(`/votes/${suggestionId}`);
    return response.data;
  },
};

export default api;
