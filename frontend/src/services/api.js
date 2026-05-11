import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

export const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const getStatus = async () => {
  const response = await client.get('/api/status');
  return response.data;
};

export const getHistory = async ({ limit = 100, offset = 0 } = {}) => {
  const response = await client.get('/api/history', {
    params: { limit, offset },
  });
  return response.data;
};

export const sendCommand = async (command, params = {}) => {
  const response = await client.post('/api/command', {
    command,
    params,
  });
  return response.data;
};
