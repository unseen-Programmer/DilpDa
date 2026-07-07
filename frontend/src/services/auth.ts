import { apiClient } from "./api";
import type {
  AuthResponse,
  ForgotPasswordRequest,
  LoginRequest,
  OTPVerificationRequest,
  RegisterRequest,
  StudentVerificationRequest,
  User,
  UserRole,
} from "../types/auth";

type BackendUser = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  role: UserRole;
  is_email_verified: boolean;
};

type BackendAuthResponse = {
  user: BackendUser;
  tokens: {
    access: string;
    refresh: string;
  };
};

export type ChangePasswordRequest = {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
};

function mapUser(user: BackendUser): User {
  const fullName = [user.first_name, user.last_name]
    .filter(Boolean)
    .join(" ")
    .trim();

  return {
    id: user.id,
    fullName,
    email: user.email,
    phone: user.phone_number,
    role: user.role,
    isVerified: user.is_email_verified,
  };
}

function mapAuthResponse(response: BackendAuthResponse): AuthResponse {
  return {
    user: mapUser(response.user),
    tokens: response.tokens,
  };
}

function splitFullName(fullName: string) {
  const parts = fullName.trim().split(/\s+/);
  const firstName = parts.shift() ?? "";

  return {
    firstName,
    lastName: parts.join(" "),
  };
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await apiClient.post<BackendAuthResponse>(
    "/accounts/login/",
    data,
  );

  return mapAuthResponse(response.data);
}

export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const { firstName, lastName } = splitFullName(data.fullName);

  const response = await apiClient.post<BackendAuthResponse>(
    "/accounts/register/",
    {
      email: data.email,
      password: data.password,
      password_confirm: data.confirmPassword,
      first_name: firstName,
      last_name: lastName,
      phone_number: data.phone,
      role: "CUSTOMER",
    },
  );

  return mapAuthResponse(response.data);
}

export async function logout(refreshToken: string) {
  await apiClient.post("/accounts/logout/", {
    refresh: refreshToken,
  });
}

export async function refreshToken(refreshTokenValue: string) {
  const response = await apiClient.post<{
    access: string;
    refresh?: string;
  }>("/accounts/token/refresh/", {
    refresh: refreshTokenValue,
  });

  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<BackendUser>("/accounts/me/");

  return mapUser(response.data);
}

export async function changePassword(data: ChangePasswordRequest) {
  const response = await apiClient.post<{ detail: string }>(
    "/accounts/change-password/",
    {
      current_password: data.currentPassword,
      new_password: data.newPassword,
      new_password_confirm: data.confirmPassword,
    },
  );

  return response.data;
}

export async function forgotPassword(data: ForgotPasswordRequest) {
  void data;

  return {
    success: true,
  };
}

export async function verifyOTP(data: OTPVerificationRequest) {
  void data;

  return {
    success: true,
  };
}

export async function submitStudentVerification(
  data: StudentVerificationRequest,
) {
  void data;

  return {
    success: true,
  };
}
