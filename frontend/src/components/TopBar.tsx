import { useLayoutEffect, useRef, useState, type ChangeEvent } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { useTheme } from "../theme/ThemeProvider";
import { useMotion, type MotionLevel } from "../theme/MotionProvider";
import { useBackendPing } from "../api/useBackendPing";
import { useAuth } from "../auth/AuthProvider";
import "./TopBar.css";

const MODE_LABEL: Record<"light" | "dark", string> = {
  light: "Claro",
  dark: "Oscuro",
};

const MOTION_LABEL: Record<MotionLevel, string> = {
  alta: "Alta",
  media: "Media",
  off: "Sin animaciones",
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
  const { level, setLevel, systemForcesReduced } = useMotion();
  const { state } = useBackendPing();
  const { user, isAuthed, isAnonymous, logout, exitAnonymously } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();

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

  function handleMotionChange(event: ChangeEvent<HTMLSelectElement>) {
    setLevel(event.target.value as MotionLevel);
  }

  const navRef = useRef<HTMLElement>(null);
  const [pillStyle, setPillStyle] = useState<{ left: number; width: number; visible: boolean }>({
    left: 0,
    width: 0,
    visible: false,
  });

  // Pill Nav (05/08/2026, veredicto final tras la exploración de
  // frontend/src/experimental/ — ver README.md ahí): la cápsula desliza
  // detrás del NavLink activo. A diferencia de la demo experimental (que
  // usaba botones con estado interno, un tab-switcher de mentira), acá los
  // links son NavLink reales — la ruta manda, no un estado local — así que
  // la posición de la cápsula se mide del DOM real después de cada render
  // en vez de derivarse de un índice. Ninguno de los dos links coincide con
  // rutas como /stream, /results, /ranking (TopBar nunca linkeó a esas) —
  // la cápsula se oculta en vez de quedarse en una posición vieja.
  useLayoutEffect(() => {
    const nav = navRef.current;
    if (!nav) return;
    const active = nav.querySelector<HTMLElement>(".topbar__link--active");
    if (!active) {
      setPillStyle((prev) => ({ ...prev, visible: false }));
      return;
    }
    setPillStyle({ left: active.offsetLeft, width: active.offsetWidth, visible: true });
  }, [pathname, isAuthed, isAnonymous, user]);

  return (
    <header className="topbar">
      <span className="logo">METIS</span>

      <nav ref={navRef} className="topbar__nav">
        {pillStyle.visible && (
          <span
            className="topbar__pill-indicator"
            style={{ left: pillStyle.left, width: pillStyle.width }}
            aria-hidden="true"
          />
        )}
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
            <span
              data-testid="user-email"
              className="fn topbar__email"
              title={user.email}
            >
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

        {/* A3 (plan post-avance) — selector de intensidad de animación,
            al lado del toggle de tema. Con el sistema pidiendo movimiento
            reducido, el nivel efectivo ya es "off" sin importar lo elegido
            acá (MotionProvider) — el selector queda habilitado igual (el
            usuario puede seguir ajustando su preferencia para cuando el
            sistema deje de pedirlo), pero lo dice explícitamente en vez de
            comportarse como si no hiciera nada. */}
        <span className="topbar__motion-select">
          <label htmlFor="motion-level" className="fn">
            Movimiento
          </label>
          <select
            id="motion-level"
            value={level}
            onChange={handleMotionChange}
            title={
              systemForcesReduced
                ? "Tu sistema pide movimiento reducido — se aplica igual que \"Sin animaciones\" mientras esa preferencia esté activa."
                : undefined
            }
          >
            <option value="alta">{MOTION_LABEL.alta}</option>
            <option value="media">{MOTION_LABEL.media}</option>
            <option value="off">{MOTION_LABEL.off}</option>
          </select>
          {systemForcesReduced && (
            <span className="fn" data-testid="motion-system-note">
              (tu sistema pide movimiento reducido)
            </span>
          )}
        </span>

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
