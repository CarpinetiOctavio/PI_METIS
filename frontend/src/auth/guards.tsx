import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthProvider";

/** Envuelve rutas exclusivas de CU-01 (docencia). Redirige a la puerta de entrada sin sesión. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthed, isLoading } = useAuth();

  if (isLoading) return null;
  if (!isAuthed) return <Navigate to="/" replace />;
  return <>{children}</>;
}

/** Envuelve la puerta de entrada: si ya hay sesión, saltea directo a config. */
export function RedirectIfAuthed({ children }: { children: ReactNode }) {
  const { isAuthed, isLoading } = useAuth();

  if (isLoading) return null;
  if (isAuthed) return <Navigate to="/config" replace />;
  return <>{children}</>;
}
