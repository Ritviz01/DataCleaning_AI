import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for large datasets processing
  headers: {
    "Content-Type": "application/json",
  },
});

// Configure simple retry mechanism
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as InternalAxiosRequestConfig & { _retryCount?: number };
    
    // Only retry on network errors or 5xx server errors
    const shouldRetry =
      config &&
      (!error.response || error.response.status >= 500) &&
      (!config._retryCount || config._retryCount < 2);

    if (shouldRetry) {
      config._retryCount = (config._retryCount || 0) + 1;
      // Linear delay backoff: 1s, then 2s
      const delay = config._retryCount * 1000;
      await new Promise((resolve) => setTimeout(resolve, delay));
      return api(config);
    }
    
    return Promise.reject(error);
  }
);
