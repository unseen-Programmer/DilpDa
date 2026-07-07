import { useRef } from "react";

type OTPInputProps = {
  value: string[];
  onChange: (value: string[]) => void;
};

export function OTPInput({
  value,
  onChange,
}: OTPInputProps) {
  const inputs = useRef<(HTMLInputElement | null)[]>([]);

  const handleChange = (
    index: number,
    inputValue: string,
  ) => {
    if (!/^\d?$/.test(inputValue)) return;

    const updated = [...value];
    updated[index] = inputValue;

    onChange(updated);

    if (inputValue && index < 5) {
      inputs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (
    index: number,
    e: React.KeyboardEvent<HTMLInputElement>,
  ) => {
    if (
      e.key === "Backspace" &&
      !value[index] &&
      index > 0
    ) {
      inputs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (
    e: React.ClipboardEvent<HTMLInputElement>,
  ) => {
    e.preventDefault();

    const pasted = e.clipboardData
      .getData("text")
      .replace(/\D/g, "")
      .slice(0, 6);

    if (!pasted) return;

    const updated = [...value];

    pasted.split("").forEach((digit, i) => {
      updated[i] = digit;
    });

    onChange(updated);

    inputs.current[Math.min(pasted.length, 5)]?.focus();
  };

  return (
    <div className="flex justify-center gap-3">
      {value.map((digit, index) => (
        <input
          key={index}
          ref={(el) => {
            inputs.current[index] = el;
          }}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={digit}
          onChange={(e) =>
            handleChange(index, e.target.value)
          }
          onKeyDown={(e) =>
            handleKeyDown(index, e)
          }
          onPaste={handlePaste}
          className="
            h-14
            w-14
            rounded-2xl
            border
            border-[var(--app-border)]
            bg-[var(--app-surface)]
            text-center
            text-xl
            font-bold
            outline-none
            transition
            focus:border-brand-primary
            focus:ring-2
            focus:ring-brand-primary/30
          "
        />
      ))}
    </div>
  );
}