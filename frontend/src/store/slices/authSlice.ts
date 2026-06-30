import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export type UserRole = "CUSTOMER" | "RESTAURANT_OWNER" | "DELIVERY_PARTNER" | "ADMIN";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  role: UserRole | null;
  isAuthenticated: boolean;
};

const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
  role: null,
  isAuthenticated: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setCredentials(
      state,
      action: PayloadAction<{
        accessToken: string;
        refreshToken: string;
        role: UserRole;
      }>,
    ) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.role = action.payload.role;
      state.isAuthenticated = true;
    },
    clearCredentials(state) {
      state.accessToken = null;
      state.refreshToken = null;
      state.role = null;
      state.isAuthenticated = false;
    },
  },
});

export const { clearCredentials, setCredentials } = authSlice.actions;
export default authSlice.reducer;
