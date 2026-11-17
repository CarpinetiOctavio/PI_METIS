// A3 (plan post-avance) — "no basta con no animar, hay que no MONTAR los
// fondos en absoluto" con el nivel "off". Los tres fondos leen su propio
// useMotion() para la densidad, pero la decisión de montarlos o no vive acá.
import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "../theme/ThemeProvider";
import { MotionProvider } from "../theme/MotionProvider";
import { AuthProvider } from "../auth/AuthProvider";
import { RootLayout } from "./RootLayout";

function Probe() {
  return <div>contenido</div>;
}

function stubFetch() {
  vi.stubGlobal(
    "fetch",
    vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 401,
        json: () => Promise.resolve({}),
      }),
    ),
  );
}

function renderRootLayout(motionLevel: "alta" | "media" | "off", path = "/config") {
  if (motionLevel !== "alta") {
    localStorage.setItem("metis-motion-level", motionLevel);
  }
  stubFetch();
  return render(
    <ThemeProvider>
      <MotionProvider>
        <MemoryRouter initialEntries={[path]}>
          <AuthProvider>
            <Routes>
              <Route element={<RootLayout />}>
                <Route path="/" element={<Probe />} />
                <Route path="/config" element={<Probe />} />
              </Route>
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      </MotionProvider>
    </ThemeProvider>,
  );
}

describe("RootLayout — fondos animados según el nivel de movimiento", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("con nivel 'alta' (default), monta ThreadsBackground y DotFieldBackground fuera de '/'", async () => {
    const { container } = renderRootLayout("alta", "/config");
    await screen.findByText("contenido");
    expect(container.querySelectorAll("canvas")).toHaveLength(2);
  });

  it("con nivel 'alta' en '/', monta ThreadsBackground y GridScanBackground", async () => {
    const { container } = renderRootLayout("alta", "/");
    await screen.findByText("contenido");
    expect(container.querySelectorAll("canvas")).toHaveLength(2);
  });

  it("con nivel 'media', los fondos se conservan (solo cambia su densidad interna)", async () => {
    const { container } = renderRootLayout("media", "/config");
    await screen.findByText("contenido");
    expect(container.querySelectorAll("canvas")).toHaveLength(2);
  });

  // El caso central de A3: "off" no monta ningún canvas, en ninguna ruta.
  it("con nivel 'off', no monta ningún fondo animado fuera de '/'", async () => {
    const { container } = renderRootLayout("off", "/config");
    await screen.findByText("contenido");
    expect(container.querySelectorAll("canvas")).toHaveLength(0);
  });

  it("con nivel 'off', no monta ningún fondo animado en '/'", async () => {
    const { container } = renderRootLayout("off", "/");
    await screen.findByText("contenido");
    expect(container.querySelectorAll("canvas")).toHaveLength(0);
  });
});
