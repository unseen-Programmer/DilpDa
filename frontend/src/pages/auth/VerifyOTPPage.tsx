import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { AuthCard } from "../../components/auth/AuthCard";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { OTPInput } from "../../components/auth/OTPInput";
import { Button } from "../../components/ui";
import { useAuth } from "../../hooks/useAuth";

const OTP_LENGTH = 6;
const RESEND_SECONDS = 60;

export function VerifyOTPPage() {
  const { loading, verifyOTP } = useAuth();

  const [otp, setOtp] = useState<string[]>(
    Array.from({ length: OTP_LENGTH }, () => ""),
  );
  const [secondsRemaining, setSecondsRemaining] =
    useState(RESEND_SECONDS);

  useEffect(() => {
    if (secondsRemaining <= 0) return;

    const timer = window.setInterval(() => {
      setSecondsRemaining((seconds) => Math.max(seconds - 1, 0));
    }, 1000);

    return () => window.clearInterval(timer);
  }, [secondsRemaining]);

  const formattedSeconds = secondsRemaining
    .toString()
    .padStart(2, "0");

  const handleResend = () => {
    setSecondsRemaining(RESEND_SECONDS);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    await verifyOTP({
      email: "",
      otp: otp.join(""),
    });
  };

  return (
    <AuthLayout
      title="Verify OTP"
      subtitle="Enter the 6-digit verification code sent to your registered email."
    >
      <AuthCard
        title="Verify OTP"
        subtitle="Enter the code to continue with password recovery."
      >
        <form className="space-y-6" onSubmit={handleSubmit}>
          <OTPInput value={otp} onChange={setOtp} />

          <div className="text-center text-sm text-[var(--app-muted)]">
            {secondsRemaining > 0 ? (
              <span>Resend OTP in 00:{formattedSeconds}</span>
            ) : (
              <button
                type="button"
                className="font-semibold text-brand-primary transition hover:text-brand-secondary"
                onClick={handleResend}
              >
                Resend OTP
              </button>
            )}
          </div>

          <Button type="submit" isLoading={loading} className="w-full">
            Verify OTP
          </Button>

          <p className="text-center text-sm text-[var(--app-text)]">
            Wrong email?{" "}
            <Link
              to="/forgot-password"
              className="font-semibold text-brand-primary"
            >
              Back to Forgot Password
            </Link>
          </p>
        </form>
      </AuthCard>
    </AuthLayout>
  );
}
