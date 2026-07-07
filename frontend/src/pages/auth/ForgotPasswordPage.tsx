import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";

import { AuthCard } from "../../components/auth/AuthCard";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { Button, Input } from "../../components/ui";
import { useAuth } from "../../hooks/useAuth";
import type { ForgotPasswordRequest } from "../../types/auth";

export function ForgotPasswordPage() {
  const { forgotPassword, loading } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordRequest>();

  const onSubmit = async ({ email }: ForgotPasswordRequest) => {
    await forgotPassword({
      email,
    });
  };

  return (
    <AuthLayout
      title="Forgot Password"
      subtitle="Enter your registered email address to receive a One-Time Password (OTP) for password recovery."
    >
      <AuthCard
        title="Forgot Password"
        subtitle="Enter your college email to recover your account."
      >
        <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <Input
            label="College Email"
            type="email"
            placeholder="student@cit.ac.in"
            autoComplete="email"
            error={errors.email?.message}
            {...register("email", {
              required: "College email is required",
              pattern: {
                value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: "Enter a valid email address",
              },
            })}
          />

          <Button type="submit" isLoading={loading} className="w-full">
            Send OTP
          </Button>

          <p className="text-center text-sm text-[var(--app-text)]">
            Remember your password?{" "}
            <Link to="/login" className="font-semibold text-brand-primary">
              Back to Login
            </Link>
          </p>
        </form>
      </AuthCard>
    </AuthLayout>
  );
}
