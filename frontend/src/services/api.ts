import axios from "axios";

import { env } from "../config/env";
import type { RootState } from "../store/store";

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

export function attachAuthInterceptors(getState: () => RootState) {
  apiClient.interceptors.request.use((config) => {
    const token = getState().auth.accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
}
