import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/Login";
import DashboardPage from "./pages/Dashboard";
import GroceriesPage from "./pages/Groceries";
import UsersPage from "./pages/Users";
import ItemsPage from "./pages/Items";
import IncomesPage from "./pages/Incomes";
import { RequireAdmin, RequireAuth } from "./components/RouteGuards";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<RequireAuth><DashboardPage /></RequireAuth>} />
      <Route path="/groceries" element={<RequireAdmin><GroceriesPage /></RequireAdmin>} />
      <Route path="/users" element={<RequireAdmin><UsersPage /></RequireAdmin>} />
      <Route path="/items" element={<RequireAuth><ItemsPage /></RequireAuth>} />
      <Route path="/incomes" element={<RequireAuth><IncomesPage /></RequireAuth>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
