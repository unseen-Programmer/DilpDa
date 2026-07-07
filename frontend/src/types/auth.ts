export type UserRole =
  | "CUSTOMER"
  | "RESTAURANT_OWNER"
  | "DELIVERY_PARTNER"
  | "ADMIN";

export interface User {
  id: number;
  fullName: string;
  email: string;
  phone: string;
  role: UserRole;
  isVerified: boolean;
  profileImage?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  fullName: string;
  email: string;
  phone: string;
  password: string;
  confirmPassword: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface OTPVerificationRequest {
  email: string;
  otp: string;
}

export interface ResetPasswordRequest {
  email: string;
  otp: string;
  password: string;
  confirmPassword: string;
}

export interface StudentVerificationRequest {
  studentId: File | null;
  rollNumber: string;
  department: string;
  semester: string;
  collegeName: string;
}