import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import type { RegisterRequest } from "../../types/auth";
import { Button, Input } from "../ui";
import { PasswordStrength } from "./PasswordStrength";

type RegisterFormValues = RegisterRequest & {
  terms: boolean;
};

export function RegisterForm() {
  const { loading, register: registerUser } = useAuth();

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    defaultValues: {
      terms: false,
    },
  });

  const password = watch("password") ?? "";

  const onSubmit = async ({ terms, ...data }: RegisterFormValues) => {
    void terms;
    await registerUser(data);
  };

  return (
    <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
      <Input
        label="Full Name"
        type="text"
        placeholder="Enter your full name"
        autoComplete="name"
        error={errors.fullName?.message}
        {...register("fullName", {
          required: "Full name is required",
          minLength: {
            value: 3,
            message: "Full name must be at least 3 characters",
          },
        })}
      />

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

      <Input
        label="Phone Number"
        type="tel"
        placeholder="10 digit phone number"
        autoComplete="tel"
        inputMode="numeric"
        error={errors.phone?.message}
        {...register("phone", {
          required: "Phone number is required",
          pattern: {
            value: /^\d{10}$/,
            message: "Phone number must be 10 digits",
          },
        })}
      />

      <div className="space-y-3">
        <div className="relative">
          <Input
            label="Password"
            type={showPassword ? "text" : "password"}
            placeholder="Create a password"
            autoComplete="new-password"
            error={errors.password?.message}
            className="pr-20"
            {...register("password", {
              required: "Password is required",
              minLength: {
                value: 8,
                message: "Password must be at least 8 characters",
              },
            })}
          />

          <button
            type="button"
            className="absolute right-4 top-[42px] text-xs font-semibold text-brand-primary transition hover:text-brand-secondary"
            onClick={() => setShowPassword((value) => !value)}
          >
            {showPassword ? "Hide" : "Show"}
          </button>
        </div>

        <PasswordStrength password={password} />
      </div>

      <div className="relative">
        <Input
          label="Confirm Password"
          type={showConfirmPassword ? "text" : "password"}
          placeholder="Confirm your password"
          autoComplete="new-password"
          error={errors.confirmPassword?.message}
          className="pr-20"
          {...register("confirmPassword", {
            required: "Confirm password is required",
            validate: (value) =>
              value === password || "Passwords do not match",
          })}
        />

        <button
          type="button"
          className="absolute right-4 top-[42px] text-xs font-semibold text-brand-primary transition hover:text-brand-secondary"
          onClick={() => setShowConfirmPassword((value) => !value)}
        >
          {showConfirmPassword ? "Hide" : "Show"}
        </button>
      </div>

      <label className="flex items-start gap-3 text-sm font-medium text-[var(--app-text)]">
        <input
          type="checkbox"
          className="mt-1 h-4 w-4 rounded border-[var(--app-border)] accent-[var(--app-primary)]"
          {...register("terms", {
            required: "You must agree to the Terms & Conditions",
          })}
        />
        <span>
          I agree to the Terms &amp; Conditions
          {errors.terms ? (
            <span className="block pt-1 text-xs font-semibold text-brand-danger">
              {errors.terms.message}
            </span>
          ) : null}
        </span>
      </label>

      <Button isLoading={loading} className="w-full" type="submit">
        Register
      </Button>

      <p className="text-center text-sm text-[var(--app-text)]">
        Already have an account?{" "}
        <Link to="/login" className="font-semibold text-brand-primary">
          Login
        </Link>
      </p>
    </form>
  );
}
