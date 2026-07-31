import { Outlet, useLocation } from "react-router-dom";
import { TopBar } from "./TopBar";
import { DotFieldBackground } from "../theme/backgrounds/DotFieldBackground";

export function RootLayout() {
  // La puerta de entrada ("/") tiene su propio fondo (GridScanBackground,
  // montado en EntryPage) — son hermanos, no se superponen (plan pasada4 §4:
  // "distinto protagonismo" en cada pantalla, nunca los dos fondos a la vez).
  const { pathname } = useLocation();
  const showDotField = pathname !== "/";

  return (
    <div className="app-shell">
      {showDotField && <DotFieldBackground />}
      <TopBar />
      <main style={{ padding: "20px" }}>
        <Outlet />
      </main>
    </div>
  );
}
