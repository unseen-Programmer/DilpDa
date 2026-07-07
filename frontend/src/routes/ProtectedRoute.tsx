import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAppSelector } from "../store/hooks";
import type { UserRole } from "../store/slices/authSlice";

type ProtectedRouteProps = {
  allowedRoles?: UserRole[];
  children: ReactNode;
};

const roleRedirects: Record<UserRole, string> = {
  CUSTOMER: "/app",
  RESTAURANT_OWNER: "/owner",
  DELIVERY_PARTNER: "/delivery",
  ADMIN: "/admin",
};

export function ProtectedRoute({ allowedRoles, children }: ProtectedRouteProps) {
  const location = useLocation();
  const { isAuthenticated, role } = useAppSelector((state) => state.auth);

  if (!isAuthenticated) {
    return <Navigate replace state={{ from: location }} to="/login" />;
  }

  if (allowedRoles && (!role || !allowedRoles.includes(role))) {
    return <Navigate replace to={role ? roleRedirects[role] : "/login"} />;
  }

  return children;
}
