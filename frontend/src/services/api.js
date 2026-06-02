import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const productApi = {
  getProducts: async () => {
    const response = await apiClient.get('/products/');
    return response.data;
  },
  getProduct: async (id) => {
    const response = await apiClient.get(`/products/${id}`);
    return response.data;
  },
  addProduct: async (productData) => {
    const response = await apiClient.post('/products/', productData);
    return response.data;
  },
  updateProduct: async (id, productData) => {
    const response = await apiClient.put(`/products/${id}`, productData);
    return response.data;
  },
  deleteProduct: async (id) => {
    const response = await apiClient.delete(`/products/${id}`);
    return response.data;
  },
  forceScrape: async (id) => {
    const response = await apiClient.post(`/products/${id}/scrape`);
    return response.data;
  },
};

export const settingsApi = {
  getSettings: async () => {
    const response = await apiClient.get('/settings/');
    return response.data;
  },
  updateSettings: async (settingsData) => {
    const response = await apiClient.post('/settings/', settingsData);
    return response.data;
  },
};
