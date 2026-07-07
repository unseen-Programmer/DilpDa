import { useState } from "react";
import { useForm } from "react-hook-form";
import { FiEye, FiEyeOff } from "react-icons/fi";
import { Link } from "react-router-dom";

import { Button, Input } from "../ui";
import { useAuth } from "../../hooks/useAuth";
import type { LoginRequest } from "../../types/auth";

export function LoginForm() {
  const { login, loading } = useAuth();

  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginRequest>();

  const onSubmit = async (data: LoginRequest) => {
    try {
      await login(data);

      // Backend integration comes later
      console.log("Logged In");
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <form
      className="space-y-6"
      onSubmit={handleSubmit(onSubmit)}
    >
      <Input
        label="College Email"
        type="email"
        placeholder="student@cit.ac.in"
        error={errors.email?.message}
        {...register("email", {
          required: "Email is required",
        })}
      />

      <div className="relative">
        <Input
          label="Password"
          type={showPassword ? "text" : "password"}
          placeholder="Enter password"
          error={errors.password?.message}
          {...register("password", {
            required: "Password is required",
          })}
        />

        <button
          type="button"
          onClick={() =>
            setShowPassword(!showPassword)
          }
          className="absolute right-4 top-[42px]"
        >
          {showPassword ? (
            <FiEyeOff />
          ) : (
            <FiEye />
          )}
        </button>
      </div>

      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" />
          Remember Me
        </label>

        <Link
          to="/forgot-password"
          className="text-sm font-semibold text-brand-primary"
        >
          Forgot Password?
        </Link>
      </div>

      <Button
        type="submit"
        isLoading={loading}
        className="w-full"
      >
        Login
      </Button>

      <div className="relative py-2">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-[var(--app-border)]" />
        </div>

        <div className="relative flex justify-center">
          <span className="bg-[var(--app-surface)] px-3 text-sm text-brand-muted">
            OR
          </span>
        </div>
      </div>

      <Button
        variant="secondary"
        type="button"
        className="w-full"
      >
        Continue with Google
      </Button>

      <p className="text-center text-sm">
        Don't have an account?{" "}
        <Link
          to="/register"
          className="font-semibold text-brand-primary"
        >
          Register
        </Link>
      </p>
    </form>
  );
}
