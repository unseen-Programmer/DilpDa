import { Route, Routes } from "react-router-dom";

import { AdminLayout, CustomerLayout, DeliveryLayout, RestaurantOwnerLayout } from "../layouts";
import { FoundationScreen } from "../pages/system/FoundationScreen";
import { LoadingScreen } from "../pages/system/LoadingScreen";
import { NotFoundPage } from "../pages/system/NotFoundPage";
import { ProtectedRoute } from "./ProtectedRoute";

export function AppRouter() {
  return (
    <Routes>
      <Route element={<FoundationScreen />} path="/" />
      <Route element={<LoadingScreen />} path="/loading" />
      <Route
        element={
          <ProtectedRoute allowedRoles={["CUSTOMER"]}>
            <CustomerLayout />
          </ProtectedRoute>
        }
        path="/app/*"
      />
      <Route
        element={
          <ProtectedRoute allowedRoles={["RESTAURANT_OWNER"]}>
            <RestaurantOwnerLayout />
          </ProtectedRoute>
        }
        path="/owner/*"
      />
      <Route
        element={
          <ProtectedRoute allowedRoles={["DELIVERY_PARTNER"]}>
            <DeliveryLayout />
          </ProtectedRoute>
        }
        path="/delivery/*"
      />
      <Route
        element={
          <ProtectedRoute allowedRoles={["ADMIN"]}>
            <AdminLayout />
          </ProtectedRoute>
        }
        path="/admin/*"
      />
      <Route element={<NotFoundPage />} path="/404" />
      <Route element={<NotFoundPage />} path="*" />
    </Routes>
  );
}
