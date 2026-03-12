const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const createApiClient = (getToken) => {
  const request = async (url, options = {}) => {
    const token = await getToken();
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_URL}${url}`, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }
    
    return response.json();
  };
  
  return {
    get: (url, options) => request(url, { ...options, method: 'GET' }),
    post: (url, data, options) => request(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    }),
    put: (url, data, options) => request(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    patch: (url, data, options) => request(url, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (url, options) => request(url, { ...options, method: 'DELETE' }),
  };
};
