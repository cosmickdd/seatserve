/**
 * API Configuration
 * Centralized configuration for API endpoints
 * In production, defaults to relative /api path (same domain)
 */

const getApiBaseUrl = () => {
  // Check if VITE_API_URL is set (via environment variable during build)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // In production with same domain, use relative path
  if (import.meta.env.PROD) {
    return '/api';
  }
  
  // Development: default to localhost
  return 'http://localhost:8000/api';
};

export const API_BASE_URL = getApiBaseUrl();
