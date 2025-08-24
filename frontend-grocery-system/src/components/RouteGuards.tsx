import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../lib/auth";

export function RequireAuth({ children }: { children: JSX.Element }) {
  const { user } = useAuth();
  const location = useLocation();
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}

export function RequireAdmin({ children }: { children: JSX.Element }) {
  const { user } = useAuth();
  const location = useLocation();
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (user.user_type !== "admin") {
    return <Navigate to="/" replace />;
  }
  return children;
}


