// Cubre F1 — el ciclo de vida REAL de StreamPage con el hook REAL, bajo
// StrictMode. Es la franja que StreamPage.test.tsx (que mockea el hook) y
// sse.test.ts (que testea el hook sin componente) dejan sin cubrir entre
// los dos. Ver docs/frontend/informe-diagnostico-ui-rota.md §5.1.
import { describe, expect, it, vi, beforeEach } from "vitest";
import { StrictMode } from "react";
import { render } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { StreamPage } from "./StreamPage";
import type { AnalysisStreamForm } from "../../api/types";

const abortSpy = vi.fn();

vi.mock("@microsoft/fetch-event-source", () => ({
  fetchEventSource: vi.fn((_url: string, opts: { signal: AbortSignal }) => {
    opts.signal.addEventListener("abort", abortSpy);
    return new Promise(() => {}); // nunca resuelve: simula un stream abierto
  }),
}));

function makeForm(): AnalysisStreamForm {
  return {
    archivo: new File(["anio,caudal\n1980,100"], "serie.csv", { type: "text/csv" }),
    columna_x: "anio",
    columna_y: "caudal",
    tipo_variable: "caudal_precipitacion",
    modo: "experto",
    cramer_particion: "default",
  };
}

function renderUnderStrictMode() {
  return render(
    <StrictMode>
      <MemoryRouter initialEntries={[{ pathname: "/stream", state: { form: makeForm() } }]}>
        <Routes>
          <Route path="/stream" element={<StreamPage />} />
          <Route path="/config" element={<div>config</div>} />
        </Routes>
      </MemoryRouter>
    </StrictMode>,
  );
}

describe("StreamPage — ciclo de vida bajo StrictMode", () => {
  beforeEach(() => abortSpy.mockClear());

  it("deja exactamente un stream vivo tras el doble montaje de StrictMode", async () => {
    const { fetchEventSource } = await import("@microsoft/fetch-event-source");
    const mocked = vi.mocked(fetchEventSource);
    mocked.mockClear();

    renderUnderStrictMode();

    // StrictMode puede arrancarlo dos veces (aceptable, el primero se aborta),
    // pero NO puede quedar cero streams vivos.
    const abiertos = mocked.mock.calls.length;
    const abortados = abortSpy.mock.calls.length;
    expect(abiertos - abortados).toBe(1);
  });

  it("aborta el stream al desmontar de verdad", () => {
    const { unmount } = renderUnderStrictMode();
    abortSpy.mockClear();
    unmount();
    expect(abortSpy).toHaveBeenCalled();
  });
});
