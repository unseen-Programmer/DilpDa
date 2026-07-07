import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type { User, UserRole } from "../../types/auth";

const AUTH_STORAGE_KEY = "dilpda.auth";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  role: UserRole | null;
  user: User | null;
  isAuthenticated: boolean;
};

function loadInitialState(): AuthState {
  const emptyState: AuthState = {
    accessToken: null,
    refreshToken: null,
    role: null,
    user: null,
    isAuthenticated: false,
  };

  try {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!stored) return emptyState;

    const parsed = JSON.parse(stored) as Partial<AuthState>;

    return {
      accessToken: parsed.accessToken ?? null,
      refreshToken: parsed.refreshToken ?? null,
      role: parsed.role ?? parsed.user?.role ?? null,
      user: parsed.user ?? null,
      isAuthenticated: Boolean(parsed.accessToken),
    };
  } catch {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    return emptyState;
  }
}

function persistState(state: AuthState) {
  localStorage.setItem(
    AUTH_STORAGE_KEY,
    JSON.stringify({
      accessToken: state.accessToken,
      refreshToken: state.refreshToken,
      role: state.role,
      user: state.user,
      isAuthenticated: state.isAuthenticated,
    }),
  );
}

function clearPersistedState() {
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

const initialState: AuthState = loadInitialState();

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setCredentials(
      state,
      action: PayloadAction<{
        accessToken: string;
        refreshToken: string;
        user: User;
      }>,
    ) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.role = action.payload.user.role;
      state.user = action.payload.user;
      state.isAuthenticated = true;
      persistState(state);
    },
    setAccessToken(state, action: PayloadAction<string>) {
      state.accessToken = action.payload;
      state.isAuthenticated = true;
      persistState(state);
    },
    setTokens(
      state,
      action: PayloadAction<{
        accessToken: string;
        refreshToken?: string;
      }>,
    ) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken ?? state.refreshToken;
      state.isAuthenticated = true;
      persistState(state);
    },
    setCurrentUser(state, action: PayloadAction<User>) {
      state.user = action.payload;
      state.role = action.payload.role;
      state.isAuthenticated = Boolean(state.accessToken);
      persistState(state);
    },
    clearCredentials(state) {
      state.accessToken = null;
      state.refreshToken = null;
      state.role = null;
      state.user = null;
      state.isAuthenticated = false;
      clearPersistedState();
    },
  },
});

export type { UserRole };
export const {
  clearCredentials,
  setAccessToken,
  setCredentials,
  setCurrentUser,
  setTokens,
} = authSlice.actions;
export default authSlice.reducer;
