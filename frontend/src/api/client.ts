import axios from 'axios';
import { userManager, getApiBaseUrl } from '@/lib/auth';
import { useUIStore } from '@/stores/uiStore';
import { useLocalAuthStore } from '@/stores/localAuthStore';

export const apiClient = axios.create({
  baseURL: `${getApiBaseUrl()}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

async function getToken(): Promise<string | null> {
  const store = useLocalAuthStore.getState();
  if (store.token) {
    if (store.isExpired()) {
      store.clearToken();
      return null;
    }
    return store.token;
  }

  try {
    const user = await userManager.getUser();
    if (user && !user.expired) {
      return user.access_token;
    }
  } catch {
    // ignore
  }
  return null;
}

apiClient.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;

apiClient.interceptors.response.use(
  (response) => {
    useUIStore.getState().setHasNetworkError(false);
    return response;
  },
  async (error) => {
    if (!error.response) {
      useUIStore.getState().setHasNetworkError(true);
      return Promise.reject(error);
    }

    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry && !isRefreshing) {
      originalRequest._retry = true;

      // Local auth token is expired/invalid — clear it and redirect to login
      const localStore = useLocalAuthStore.getState();
      if (localStore.token) {
        localStore.clearToken();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      // OIDC path — try silent refresh
      isRefreshing = true;
      try {
        const newUser = await userManager.signinSilent();
        isRefreshing = false;

        if (newUser?.access_token) {
          originalRequest.headers.Authorization = `Bearer ${newUser.access_token}`;
          return apiClient(originalRequest);
        }
      } catch {
        isRefreshing = false;
        window.location.href = '/';
      }
    }

    return Promise.reject(error);
  }
);
