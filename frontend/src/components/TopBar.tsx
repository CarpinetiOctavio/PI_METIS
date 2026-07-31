import { NavLink, useNavigate } from "react-router-dom";
import { useTheme } from "../theme/ThemeProvider";
import { useBackendPing } from "../api/useBackendPing";
import { useAuth } from "../auth/AuthProvider";
import "./TopBar.css";

const MODE_LABEL: Record<"light" | "dark", string> = {
  light: "Claro",
  dark: "Oscuro",
};

const BACKEND_LABEL: Record<"loading" | "ok" | "error", string> = {
  loading: "Conectando…",
  ok: "Backend conectado",
  error: "Backend no disponible",
};

function navLinkClassName({ isActive }: { isActive: boolean }): string {
  return `topbar__link${isActive ? " topbar__link--active" : ""}`;
}

export function TopBar() {
  const { mode, toggleMode } = useTheme();
  const { state } = useBackendPing();
  const { user, isAuthed, isAnonymous, logout, exitAnonymously } = useAuth();
  const navigate = useNavigate();

  // F4/F5/F6 (informe-diagnostico-ui-rota.md): antes esta barra no tenía un
  // solo link — /history y /ranking eran alcanzables únicamente tipeando la
  // URL a mano, y "Cerrar sesión" no redirigía a ningún lado.
  async function handleLogout() {
    await logout();
    navigate("/", { replace: true });
  }

  function handleExitAnonymous() {
    exitAnonymously();
    navigate("/", { replace: true });
  }

  return (
    <header className="topbar">
      <span className="logo">METIS</span>

      <nav className="topbar__nav">
        {(isAuthed || isAnonymous) && (
          <NavLink to="/config" className={navLinkClassName}>
            Nuevo análisis
          </NavLink>
        )}
        {isAuthed && user && (
          <NavLink to="/history" className={navLinkClassName}>
            Historial
          </NavLink>
        )}
      </nav>

      <div className="topbar__indicators">
        {/* C1 (G5): el estado deja de comunicarse solo por color — el texto
            de BACKEND_LABEL sigue presente siempre, el punto es un refuerzo
            visual, no el único portador de la información (regla de
            accesibilidad de Fase 2, la misma que rige A4). */}
        <span
          className={`topbar__status${state === "ok" ? " badge-live" : ""}`}
          data-testid="backend-status"
        >
          {state !== "ok" && (
            <span
              className={`topbar__dot topbar__dot--${state}`}
              aria-hidden="true"
            />
          )}
          {BACKEND_LABEL[state]}
        </span>

        {isAuthed && user && (
          <>
            <span className="topbar__sep" aria-hidden="true" />
            <span data-testid="user-email" className="fn">
              {user.email}
            </span>
            <button type="button" className="link-btn" onClick={() => void handleLogout()}>
              Cerrar sesión
            </button>
          </>
        )}
        {isAnonymous && !isAuthed && (
          <>
            <span className="topbar__sep" aria-hidden="true" />
            <button type="button" className="link-btn" onClick={handleExitAnonymous}>
              Salir
            </button>
          </>
        )}

        <span className="topbar__sep" aria-hidden="true" />

        <span className="topbar__theme-toggle">
          <span data-testid="mode-badge" className="fn">
            {MODE_LABEL[mode]}
          </span>
          <button
            type="button"
            className="topbar__toggle-btn"
            aria-label="Cambiar tema"
            onClick={toggleMode}
          >
            <span className="topbar__toggle-knob" />
          </button>
        </span>
      </div>
    </header>
  );
}
