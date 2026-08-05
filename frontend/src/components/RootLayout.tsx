import { Outlet, useLocation } from "react-router-dom";
import { TopBar } from "./TopBar";
import { DotFieldBackground } from "../theme/backgrounds/DotFieldBackground";
import { GridScanBackground } from "../theme/backgrounds/GridScanBackground";

export function RootLayout() {
  // La puerta de entrada ("/") tiene su propio fondo (GridScanBackground) —
  // son hermanos, nunca los dos fondos a la vez (plan pasada4 §4: "distinto
  // protagonismo" en cada pantalla).
  //
  // Bug encontrado en verificación manual (05/08/2026): GridScanBackground
  // vivía montado DENTRO de EntryPage, que renderiza dentro de `.route-enter`
  // más abajo. `.route-enter` tiene `animation: fade-up` sobre opacity/transform
  // — eso hace que el navegador la trate como generadora de su propio stacking
  // context Y de containing block para descendientes `position: fixed` (CSS
  // Transforms spec). El canvas fixed/inset:0 quedaba atrapado DENTRO de ese
  // contexto en vez de cubrir la página entera: pintaba detrás de sus propios
  // hermanos (`.entry`) y desplazado del viewport real. Confirmado con
  // elementFromPoint() incluso pintando el canvas a mano — nunca era el
  // elemento superior. Los dos fondos ahora viven acá, hermanos de TopBar/main,
  // nunca dentro del wrapper animado de cada ruta — igual que ya estaba
  // DotFieldBackground, que por eso nunca tuvo este problema.
  const { pathname, key } = useLocation();
  const showDotField = pathname !== "/";
  const showGridScan = pathname === "/";

  return (
    <div className="app-shell">
      {showDotField && <DotFieldBackground />}
      {showGridScan && <GridScanBackground />}
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
