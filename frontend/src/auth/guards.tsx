import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthProvider";

// D7 (pasada de mejora): antes ambos guards devolvían null mientras
// isLoading — pantalla completamente en blanco en cada carga de la app.
function AuthLoading() {
  return (
    <div className="auth-loading" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span className="visually-hidden">Cargando…</span>
    </div>
  );
}

/** Envuelve rutas exclusivas de CU-01 (docencia). Redirige a la puerta de entrada sin sesión. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthed, isLoading } = useAuth();

  if (isLoading) return <AuthLoading />;
  if (!isAuthed) return <Navigate to="/" replace />;
  return <>{children}</>;
}

/** Envuelve la puerta de entrada: si ya hay sesión, saltea directo a config. */
export function RedirectIfAuthed({ children }: { children: ReactNode }) {
  const { isAuthed, isLoading } = useAuth();

  if (isLoading) return <AuthLoading />;
  if (isAuthed) return <Navigate to="/config" replace />;
  return <>{children}</>;
}
