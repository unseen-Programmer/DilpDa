import axios, {
  AxiosError,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";

import { env } from "../config/env";
import { clearCredentials, setTokens } from "../store/slices/authSlice";
import type { AppDispatch, RootState } from "../store/store";

type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

const refreshClient = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

let interceptorAttached = false;

export function attachAuthInterceptors(
  getState: () => RootState,
  dispatch: AppDispatch,
) {
  if (interceptorAttached) return;

  interceptorAttached = true;

  apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = getState().auth.accessToken;

      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      return config;
    },
    (error) => Promise.reject(error),
  );

  apiClient.interceptors.response.use(
    (response) => response,

    async (error: AxiosError) => {
      const originalRequest = error.config as
        | RetryableRequestConfig
        | undefined;

      const refreshToken = getState().auth.refreshToken;

      if (
        error.response?.status !== 401 ||
        !originalRequest ||
        originalRequest._retry ||
        !refreshToken
      ) {
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      try {
        const response = await refreshClient.post<{
          access: string;
          refresh?: string;
        }>("/accounts/token/refresh/", {
          refresh: refreshToken,
        });

        dispatch(
          setTokens({
            accessToken: response.data.access,
            refreshToken: response.data.refresh ?? refreshToken,
          }),
        );

        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;

        return apiClient(originalRequest as AxiosRequestConfig);
      } catch (refreshError) {
        dispatch(clearCredentials());

        return Promise.reject(refreshError);
      }
    },
  );
}