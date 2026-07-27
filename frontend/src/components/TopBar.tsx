import { useTheme } from "../theme/ThemeProvider";

const MODE_LABEL: Record<"light" | "dark", string> = {
  light: "Claro",
  dark: "Oscuro",
};

export function TopBar() {
  const { mode, toggleMode } = useTheme();

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
        <span data-testid="mode-badge">{MODE_LABEL[mode]}</span>
        <button type="button" onClick={toggleMode}>
          Cambiar tema
        </button>
      </div>
    </header>
  );
}
