import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
});

export default apiClient;