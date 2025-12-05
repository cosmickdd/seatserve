import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  withCredentials: true,  // ✅ SECURE: Send cookies with requests
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized - try token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Refresh token is sent via HTTP-only cookie automatically
        await axios.post(`${API_BASE_URL}/auth/auth/refresh/`, {}, {
          withCredentials: true
        });
        
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Token refresh failed - redirect to login
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
