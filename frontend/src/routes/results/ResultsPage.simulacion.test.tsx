import { afterEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "../../auth/AuthProvider";
import { renderPage } from "../../test/renderPage";
import { makeEtapa1Datos } from "../../test/etapa1Fixtures";
import { makeEtapa1Result, makeSimulacion } from "../../test/simulacionFixtures";
import { stubFetchRouted } from "../../test/fetchStubs";
import type { CramerParticion, TipoVariable } from "../../api/types";
import { ResultsPage } from "./ResultsPage";

// Cableado del what-if de atípicos en la página (ítem A, A2): cuándo aparece el
// botón y qué pide al backend. El endpoint todavía no existe (Tanda 2), así que
// la interfaz está apagada por defecto detrás de VITE_SIMULATE_EXCLUSION.
const RECALCULAR = /Recalcular sin los puntos seleccionados/;

interface Estado {
  tipoVariable?: TipoVariable;
  cramerParticion?: CramerParticion;
  etapas?: "1" | "1,2";
}

function montar(estado: Estado = { tipoVariable: "otro" }) {
  const fetchMock = stubFetchRouted([
    { match: (url) => url.includes("/auth/me"), status: 401, body: {} },
    {
      match: (url, init) => init?.method === "POST" && url.includes("/simulate-exclusion"),
      status: 200,
      body: makeSimulacion(),
    },
  ]);
  renderPage(
    <MemoryRouter
      initialEntries={[
        {
          pathname: "/results",
          state: { result: makeEtapa1Result({ datos: makeEtapa1Datos() }), ...estado },
        },
      ]}
    >
      <AuthProvider>
        <Routes>
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
  return { fetchMock, user: userEvent.setup() };
}

function pedidoDeSimulacion(fetchMock: ReturnType<typeof stubFetchRouted>) {
  const llamada = fetchMock.mock.calls.find(([url]) => String(url).includes("/simulate-exclusion"));
  return llamada ? JSON.parse(String((llamada[1] as RequestInit).body)) : null;
}

describe("ResultsPage — what-if de atípicos", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it("con el endpoint apagado (default) no ofrece recalcular", async () => {
    montar();
    await screen.findByRole("heading", { name: "Resultados de Etapa 1" });
    expect(screen.queryByRole("button", { name: RECALCULAR })).not.toBeInTheDocument();
  });

  it("sin la configuración del análisis en el estado tampoco lo ofrece", async () => {
    vi.stubEnv("VITE_SIMULATE_EXCLUSION", "1");
    montar({});
    await screen.findByRole("heading", { name: "Resultados de Etapa 1" });
    expect(screen.queryByRole("button", { name: RECALCULAR })).not.toBeInTheDocument();
  });

  it.each([
    ["Etapa 1, partición por defecto", { tipoVariable: "otro" as const }, "otro", "default", [1]],
    [
      "Etapas 1 y 2, caudal",
      { tipoVariable: "caudal_precipitacion" as const, etapas: "1,2" as const },
      "caudal_precipitacion",
      "default",
      [1, 2],
    ],
    [
      "partición de Cramer personalizada, enviada como texto JSON",
      { tipoVariable: "otro" as const, cramerParticion: { n1_pct: 70, n2_pct: 20 } },
      "otro",
      '{"n1_pct":70,"n2_pct":20}',
      [1],
    ],
  ])("pide al backend la serie efectiva y la configuración: %s", async (_caso, estado, tipo, cramer, etapas) => {
    vi.stubEnv("VITE_SIMULATE_EXCLUSION", "1");
    const { fetchMock, user } = montar(estado);

    const casillas = await screen.findAllByRole("checkbox");
    await user.click(casillas[3]);
    await user.click(screen.getByRole("button", { name: RECALCULAR }));

    await screen.findByText("Resultados sin los puntos excluidos");
    const datos = makeEtapa1Datos();
    expect(pedidoDeSimulacion(fetchMock)).toEqual({
      serie: datos.serie_efectiva,
      anios: datos.timestamps_efectivos!.map((t) => t.anio),
      tipo_variable: tipo,
      cramer_particion: cramer,
      indices_excluidos: [3],
      etapas,
    });
  });
});
