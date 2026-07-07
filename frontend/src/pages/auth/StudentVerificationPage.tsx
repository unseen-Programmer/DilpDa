import { AuthCard } from "../../components/auth/AuthCard";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { StudentVerificationForm } from "../../components/auth/StudentVerificationForm";

export function StudentVerificationPage() {
  return (
    <AuthLayout
      title="Student Verification"
      subtitle="Verify your student identity to unlock DilpDa Pay Later and exclusive campus benefits."
    >
      <AuthCard
        title="Verify Your Identity"
        subtitle="Upload your student ID and academic details for verification."
      >
        <StudentVerificationForm />
      </AuthCard>
    </AuthLayout>
  );
}
