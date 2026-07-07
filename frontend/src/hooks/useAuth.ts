import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import * as authService from "../services/auth";
import type { ChangePasswordRequest } from "../services/auth";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import {
  clearCredentials,
  setCredentials,
  setCurrentUser,
} from "../store/slices/authSlice";
import type {
  LoginRequest,
  RegisterRequest,
  ForgotPasswordRequest,
  OTPVerificationRequest,
  StudentVerificationRequest,
  UserRole,
} from "../types/auth";

const roleRedirects: Record<UserRole, string> = {
  CUSTOMER: "/app",
  RESTAURANT_OWNER: "/owner",
  DELIVERY_PARTNER: "/delivery",
  ADMIN: "/admin",
};

function getRoleRedirect(role: UserRole) {
  return roleRedirects[role];
}

export function useAuth() {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!auth.accessToken || auth.user) return;

    authService
      .getCurrentUser()
      .then((user) => {
        dispatch(setCurrentUser(user));
      })
      .catch(() => {
        dispatch(clearCredentials());
      });
  }, [auth.accessToken, auth.user, dispatch]);

  async function login(data: LoginRequest) {
    try {
      setLoading(true);
      setError(null);

      const response = await authService.login(data);

      dispatch(
        setCredentials({
          accessToken: response.tokens.access,
          refreshToken: response.tokens.refresh,
          user: response.user,
        }),
      );
      navigate(getRoleRedirect(response.user.role), { replace: true });

      return response;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Login failed.";

      setError(message);

      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function register(data: RegisterRequest) {
    try {
      setLoading(true);
      setError(null);

      const response = await authService.register(data);

      dispatch(
        setCredentials({
          accessToken: response.tokens.access,
          refreshToken: response.tokens.refresh,
          user: response.user,
        }),
      );
      navigate(getRoleRedirect(response.user.role), { replace: true });

      return response;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Registration failed.";

      setError(message);

      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function forgotPassword(
    data: ForgotPasswordRequest,
  ) {
    try {
      setLoading(true);
      setError(null);

      return await authService.forgotPassword(data);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Failed to send reset link.";

      setError(message);

      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function verifyOTP(
    data: OTPVerificationRequest,
  ) {
    try {
      setLoading(true);
      setError(null);

      return await authService.verifyOTP(data);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "OTP verification failed.";

      setError(message);

      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function submitStudentVerification(
    data: StudentVerificationRequest,
  ) {
    try {
      setLoading(true);
      setError(null);

      return await authService.submitStudentVerification(data);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Verification failed.";

      setError(message);

      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function refreshCurrentUser() {
    const user = await authService.getCurrentUser();

    dispatch(setCurrentUser(user));

    return user;
  }

  async function changePassword(data: ChangePasswordRequest) {
    try {
      setLoading(true);
      setError(null);

      return await authService.changePassword(data);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Password change failed.";

      setError(message);

      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    try {
      if (auth.refreshToken) {
        await authService.logout(auth.refreshToken);
      }
    } finally {
      dispatch(clearCredentials());
      navigate("/login", { replace: true });
    }
  }

  return {
    user: auth.user,
    loading,
    error,
    isAuthenticated: auth.isAuthenticated,
    role: auth.role,

    login,
    register,
    forgotPassword,
    verifyOTP,
    submitStudentVerification,
    refreshCurrentUser,
    changePassword,
    logout,
  };
}
