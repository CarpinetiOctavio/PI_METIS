import { Outlet, useLocation } from "react-router-dom";
import { TopBar } from "./TopBar";
import { DotFieldBackground } from "../theme/backgrounds/DotFieldBackground";

export function RootLayout() {
  // La puerta de entrada ("/") tiene su propio fondo (GridScanBackground,
  // montado en EntryPage) — son hermanos, no se superponen (plan pasada4 §4:
  // "distinto protagonismo" en cada pantalla, nunca los dos fondos a la vez).
  const { pathname, key } = useLocation();
  const showDotField = pathname !== "/";

  return (
    <div className="app-shell">
      {showDotField && <DotFieldBackground />}
      <TopBar />
      <main style={{ padding: "20px" }}>
        {/* C2 (plan pasada4 §5): fade-up al montar cada ruta, key=location.key
            para que se dispare en cada navegación (incluso a la misma ruta
            con state distinto, no solo pathname). El contenido está en el
            DOM de inmediato — solo se anima opacity/transform, nunca se
            retrasa la aparición (misma regla de cobertura que A5). */}
        <div className="route-enter" key={key}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
