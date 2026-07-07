import { useState } from "react";
import { useForm } from "react-hook-form";

import { useAuth } from "../../hooks/useAuth";
import { Button, Input } from "../ui";

const COLLEGE_NAME = "Central Institute of Technology, Kokrajhar";
const MAX_FILE_SIZE = 5 * 1024 * 1024;
const ACCEPTED_FILE_TYPES = ["image/jpeg", "image/png", "application/pdf"];

const departments = [
  "Computer Science & Engineering",
  "Civil Engineering",
  "Mechanical Engineering",
  "Electrical Engineering",
  "Electronics & Communication",
  "Food Engineering",
  "Instrumentation Engineering",
  "Business Administration",
  "Others",
];

const semesters = ["1", "2", "3", "4", "5", "6", "7", "8"];

type StudentVerificationFormValues = {
  collegeName: string;
  department: string;
  semester: string;
  rollNumber: string;
  studentId: FileList;
};

export function StudentVerificationForm() {
  const { submitStudentVerification, loading } = useAuth();
  const [selectedFileName, setSelectedFileName] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<StudentVerificationFormValues>({
    defaultValues: {
      collegeName: COLLEGE_NAME,
      department: "",
      semester: "",
      rollNumber: "",
    },
  });

  const studentIdRegister = register("studentId", {
    required: "Student ID is required",
    validate: {
      fileType: (files) => {
        const file = files?.[0];

        return (
          !file ||
          ACCEPTED_FILE_TYPES.includes(file.type) ||
          "Only JPG, PNG, and PDF files are allowed"
        );
      },
      fileSize: (files) => {
        const file = files?.[0];

        return (
          !file ||
          file.size <= MAX_FILE_SIZE ||
          "Student ID must be 5 MB or smaller"
        );
      },
    },
  });

  const onSubmit = async (data: StudentVerificationFormValues) => {
    const studentId = data.studentId[0] ?? null;

    await submitStudentVerification({
      studentId,
      rollNumber: data.rollNumber,
      department: data.department,
      semester: data.semester,
      collegeName: data.collegeName,
    });
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
      <Input
        label="Full Name"
        placeholder="Full name will appear here"
        readOnly
      />

      <Input
        label="College Name"
        error={errors.collegeName?.message}
        {...register("collegeName", {
          required: "College name is required",
        })}
      />

      <div className="grid gap-2 text-sm font-medium text-[var(--app-text)]">
        <label htmlFor="department">Department</label>
        <select
          id="department"
          className="h-11 rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface-strong)] px-4 text-[var(--app-text)] outline-none transition focus:border-brand-accent focus:ring-4 focus:ring-[var(--app-ring)]"
          {...register("department", {
            required: "Department is required",
          })}
        >
          <option value="">Select department</option>
          {departments.map((department) => (
            <option key={department} value={department}>
              {department}
            </option>
          ))}
        </select>
        {errors.department ? (
          <span className="text-xs font-semibold text-brand-danger">
            {errors.department.message}
          </span>
        ) : null}
      </div>

      <div className="grid gap-2 text-sm font-medium text-[var(--app-text)]">
        <label htmlFor="semester">Semester</label>
        <select
          id="semester"
          className="h-11 rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface-strong)] px-4 text-[var(--app-text)] outline-none transition focus:border-brand-accent focus:ring-4 focus:ring-[var(--app-ring)]"
          {...register("semester", {
            required: "Semester is required",
          })}
        >
          <option value="">Select semester</option>
          {semesters.map((semester) => (
            <option key={semester} value={semester}>
              Semester {semester}
            </option>
          ))}
        </select>
        {errors.semester ? (
          <span className="text-xs font-semibold text-brand-danger">
            {errors.semester.message}
          </span>
        ) : null}
      </div>

      <Input
        label="Roll Number"
        placeholder="Enter your roll number"
        error={errors.rollNumber?.message}
        {...register("rollNumber", {
          required: "Roll number is required",
        })}
      />

      <div className="grid gap-2 text-sm font-medium text-[var(--app-text)]">
        <span>Student ID Upload</span>
        <label
          htmlFor="student-id"
          className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-[var(--app-border)] bg-[var(--app-surface-strong)] px-6 py-8 text-center transition hover:border-brand-primary hover:bg-brand-primary/5"
        >
          <span className="text-sm font-semibold text-brand-primary">
            Upload Student ID
          </span>
          <span className="mt-2 text-xs text-brand-muted">
            JPG, PNG, or PDF up to 5 MB
          </span>
          {selectedFileName ? (
            <span className="mt-4 max-w-full truncate text-sm font-semibold text-[var(--app-text)]">
              {selectedFileName}
            </span>
          ) : null}
        </label>
        <input
          id="student-id"
          type="file"
          accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf"
          className="sr-only"
          name={studentIdRegister.name}
          ref={studentIdRegister.ref}
          onBlur={studentIdRegister.onBlur}
          onChange={(event) => {
            studentIdRegister.onChange(event);
            setSelectedFileName(event.target.files?.[0]?.name ?? "");
          }}
        />
        {errors.studentId ? (
          <span className="text-xs font-semibold text-brand-danger">
            {errors.studentId.message}
          </span>
        ) : null}
      </div>

      <Button type="submit" isLoading={loading} className="w-full">
        Submit Verification
      </Button>
    </form>
  );
}
