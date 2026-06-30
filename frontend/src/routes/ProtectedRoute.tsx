import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAppSelector } from "../store/hooks";
import type { UserRole } from "../store/slices/authSlice";

type ProtectedRouteProps = {
  allowedRoles?: UserRole[];
  children: ReactNode;
};

export function ProtectedRoute({ allowedRoles, children }: ProtectedRouteProps) {
  const location = useLocation();
  const { isAuthenticated, role } = useAppSelector((state) => state.auth);

  if (!isAuthenticated) {
    return <Navigate replace state={{ from: location }} to="/" />;
  }

  if (allowedRoles && (!role || !allowedRoles.includes(role))) {
    return <Navigate replace to="/404" />;
  }

  return children;
}
