import { useTheme } from "../theme/ThemeProvider";
import { useBackendPing } from "../api/useBackendPing";
import { useAuth } from "../auth/AuthProvider";

const MODE_LABEL: Record<"light" | "dark", string> = {
  light: "Claro",
  dark: "Oscuro",
};

const BACKEND_LABEL: Record<"loading" | "ok" | "error", string> = {
  loading: "Conectando…",
  ok: "Backend conectado",
  error: "Backend no disponible",
};

export function TopBar() {
  const { mode, toggleMode } = useTheme();
  const { state } = useBackendPing();
  const { user, isAuthed, logout } = useAuth();

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 20px",
        borderBottom: "1px solid var(--line)",
      }}
    >
      <span style={{ fontWeight: 700, letterSpacing: "0.5px" }}>METIS</span>
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <span data-testid="backend-status">{BACKEND_LABEL[state]}</span>
        {isAuthed && user && (
          <>
            <span data-testid="user-email">{user.email}</span>
            <button type="button" onClick={() => void logout()}>
              Cerrar sesión
            </button>
          </>
        )}
        <span data-testid="mode-badge">{MODE_LABEL[mode]}</span>
        <button type="button" onClick={toggleMode}>
          Cambiar tema
        </button>
      </div>
    </header>
  );
}
