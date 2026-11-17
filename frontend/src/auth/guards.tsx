import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthProvider";

// D7 (pasada de mejora): antes ambos guards devolvían null mientras
// isLoading — pantalla completamente en blanco en cada carga de la app.
// N2 (limpieza SonarCloud): <output> ya tiene role="status" implícito —
// el role explícito era ARIA redundante sobre un elemento nativo.
function AuthLoading() {
  return (
    <output className="auth-loading" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span className="visually-hidden">Cargando…</span>
    </output>
  );
}

/** Envuelve rutas exclusivas de CU-01 (docencia). Redirige a la puerta de entrada sin sesión. */
export function RequireAuth({ children }: Readonly<{ children: ReactNode }>) {
  const { isAuthed, isLoading } = useAuth();

  if (isLoading) return <AuthLoading />;
  if (!isAuthed) return <Navigate to="/" replace />;
  return <>{children}</>;
}

/** Envuelve la puerta de entrada: si ya hay sesión, saltea directo a config. */
export function RedirectIfAuthed({ children }: Readonly<{ children: ReactNode }>) {
  const { isAuthed, isLoading } = useAuth();

  if (isLoading) return <AuthLoading />;
  if (isAuthed) return <Navigate to="/config" replace />;
  return <>{children}</>;
}

// F7 (informe-diagnostico-ui-rota.md): /config, /stream, /results, /ranking
// y /design-events no tenían NINGÚN guard — se podía entrar sin haber
// pasado nunca por la puerta de entrada, ni autenticado ni anónimo.
// constraints.md es explícito: "la distinción CU-01/CU-02 no se resuelve
// por ruta — se resuelve por presencia de JWT" — pero eso presupone que
// hubo una decisión consciente de entrar como uno u otro. Este guard no
// reintroduce esa distinción por ruta; solo exige que exista CUALQUIERA de
// las dos sesiones antes de entrar al pipeline.
/** Envuelve rutas de CU-01 o CU-02 (pipeline): exige sesión real o anónima. */
export function RequireSession({ children }: Readonly<{ children: ReactNode }>) {
  const { isAuthed, isAnonymous, isLoading } = useAuth();

  if (isLoading) return <AuthLoading />;
  if (!isAuthed && !isAnonymous) return <Navigate to="/" replace />;
  return <>{children}</>;
}
