import { AuthCard } from "../../components/auth/AuthCard";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { LoginForm } from "../../components/auth/LoginForm";

export function LoginPage() {
  return (
    <AuthLayout
      title="Welcome Back"
      subtitle="Sign in to continue to DilpDa"
    >
      <AuthCard
        title="Login"
        subtitle="Enter your college credentials to continue."
      >
        <LoginForm />
      </AuthCard>
    </AuthLayout>
  );
}
