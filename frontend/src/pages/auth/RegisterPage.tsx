import { AuthCard } from "../../components/auth/AuthCard";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { RegisterForm } from "../../components/auth/RegisterForm";

export function RegisterPage() {
  return (
    <AuthLayout
      title="Create Your Account"
      subtitle="Join DilpDa and enjoy seamless campus food ordering."
    >
      <AuthCard
        title="Register"
        subtitle="Fill in your details to create your account."
      >
        <RegisterForm />
      </AuthCard>
    </AuthLayout>
  );
}
