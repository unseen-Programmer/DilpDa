type PasswordStrengthProps = {
  password: string;
};

export function PasswordStrength({
  password,
}: PasswordStrengthProps) {
  const checks = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };

  const score = Object.values(checks).filter(Boolean).length;

  const levels = [
    {
      label: "Very Weak",
      color: "bg-red-500",
    },
    {
      label: "Weak",
      color: "bg-orange-500",
    },
    {
      label: "Medium",
      color: "bg-yellow-500",
    },
    {
      label: "Strong",
      color: "bg-lime-600",
    },
    {
      label: "Very Strong",
      color: "bg-green-600",
    },
  ];

  const current =
    score === 0 ? levels[0] : levels[Math.min(score - 1, 4)];

  return (
    <div className="space-y-4">

      <div>

        <div className="mb-2 flex items-center justify-between">

          <span className="text-sm font-medium text-brand-muted">
            Password Strength
          </span>

          <span className="text-sm font-semibold text-brand-primary">
            {current.label}
          </span>

        </div>

        <div className="h-2 overflow-hidden rounded-full bg-gray-200 dark:bg-neutral-700">

          <div
            className={`h-full rounded-full transition-all duration-500 ${current.color}`}
            style={{
              width: `${score * 20}%`,
            }}
          />

        </div>

      </div>

      <div className="grid gap-2 text-sm">

        <Requirement
          ok={checks.length}
          text="Minimum 8 characters"
        />

        <Requirement
          ok={checks.uppercase}
          text="One uppercase letter"
        />

        <Requirement
          ok={checks.lowercase}
          text="One lowercase letter"
        />

        <Requirement
          ok={checks.number}
          text="One number"
        />

        <Requirement
          ok={checks.special}
          text="One special character"
        />

      </div>

    </div>
  );
}

type RequirementProps = {
  ok: boolean;
  text: string;
};

function Requirement({
  ok,
  text,
}: RequirementProps) {
  return (
    <div
      className={`flex items-center gap-2 ${
        ok
          ? "text-green-600"
          : "text-brand-muted"
      }`}
    >
      <span>{ok ? "✔" : "○"}</span>

      <span>{text}</span>
    </div>
  );
}