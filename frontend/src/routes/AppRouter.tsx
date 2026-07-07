import { Route, Routes } from "react-router-dom";

import {
  AdminLayout,
  CustomerLayout,
  DeliveryLayout,
  RestaurantOwnerLayout,
} from "../layouts";

import { HomePage } from "../pages/customer/HomePage";
import { MenuDetailsPage } from "../pages/customer/MenuDetailsPage";
import { MenuPage } from "../pages/customer/MenuPage";
import { SearchPage } from "../pages/customer/SearchPage";

import { LoadingScreen } from "../pages/system/LoadingScreen";
import { NotFoundPage } from "../pages/system/NotFoundPage";

import { ProtectedRoute } from "./ProtectedRoute";

export function AppRouter() {
  return (
    <Routes>

      {/* ---------------- PUBLIC WEBSITE ---------------- */}

      <Route
        element={<CustomerLayout />}
        path="/"
      >
        <Route index element={<HomePage />} />
        <Route path="menu" element={<MenuPage />} />
        <Route path="menu/:foodId" element={<MenuDetailsPage />} />
        <Route path="search" element={<SearchPage />} />
      </Route>

      {/* ---------------- CUSTOMER DASHBOARD ---------------- */}

      <Route
        path="/app/*"
        element={
          <ProtectedRoute allowedRoles={["CUSTOMER"]}>
            <CustomerLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<HomePage />} />
        <Route path="menu" element={<MenuPage />} />
        <Route path="menu/:foodId" element={<MenuDetailsPage />} />
        <Route path="search" element={<SearchPage />} />
      </Route>

      {/* ---------------- RESTAURANT OWNER ---------------- */}

      <Route
        path="/owner/*"
        element={
          <ProtectedRoute allowedRoles={["RESTAURANT_OWNER"]}>
            <RestaurantOwnerLayout />
          </ProtectedRoute>
        }
      />

      {/* ---------------- DELIVERY ---------------- */}

      <Route
        path="/delivery/*"
        element={
          <ProtectedRoute allowedRoles={["DELIVERY_PARTNER"]}>
            <DeliveryLayout />
          </ProtectedRoute>
        }
      />

      {/* ---------------- ADMIN ---------------- */}

      <Route
        path="/admin/*"
        element={
          <ProtectedRoute allowedRoles={["ADMIN"]}>
            <AdminLayout />
          </ProtectedRoute>
        }
      />

      {/* ---------------- LOADING ---------------- */}

      <Route path="/loading" element={<LoadingScreen />} />

      {/* ---------------- 404 ---------------- */}

      <Route path="/404" element={<NotFoundPage />} />

      <Route path="*" element={<NotFoundPage />} />

    </Routes>
  );
}