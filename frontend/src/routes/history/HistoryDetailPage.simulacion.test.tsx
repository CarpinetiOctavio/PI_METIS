import { afterEach, describe, expect, it, vi } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { renderPage } from "../../test/renderPage";
import { makeEtapa1Datos } from "../../test/etapa1Fixtures";
import { makeEtapa2 } from "../../test/etapa2Fixtures";
import { makeEtapa1Result, makeSimulacion } from "../../test/simulacionFixtures";
import { stubFetchRouted } from "../../test/fetchStubs";
import type { AnalysisDetail } from "../../api/types";
import { HistoryDetailPage } from "./HistoryDetailPage";

// Exportar PDF (DECISIÓN 075): jsdom no implementa URL.createObjectURL.
const { obtenerPdfAnalisis, guardarPdf } = vi.hoisted(() => ({
  obtenerPdfAnalisis: vi.fn(),
  guardarPdf: vi.fn(),
}));
vi.mock("../../api/export", () => ({ obtenerPdfAnalisis, guardarPdf }));

// Bloque B de la revisión manual del 21/10/2026: el what-if de atípicos
// (DECISIÓN 071) también desde el historial, con los datos persistidos.
const RECALCULAR = /Recalcular sin los puntos seleccionados/;

const SELECCION = {
  distribucion: "gumbel",
  metodo: "momentos",
  periodos_retorno: [2, 10, 100],
  eventos_diseno: [{ periodo_retorno: 2, valor: 138.4 }],
  curva_ajuste: [{ periodo_retorno: 1.05, valor: 61.2 }],
};

function exclusion(id: string, indices: number[]) {
  return {
    id,
    creado_at: "2026-10-21T10:00:00",
    indices,
    puntos: indices.map((i) => ({ indice: i, periodo: 2000 + i, valor: 100 + i * 3 })),
    alfa: 0.1 as const,
    cramer_particion: "default" as const,
  };
}

function detalle(overrides: Partial<AnalysisDetail> = {}): AnalysisDetail {
  const datos = makeEtapa1Datos();
  return {
    id: "an-1",
    tipo_variable: "caudal_precipitacion",
    modo: "experto",
    etapas: ["1", "2"],
    created_at: "2026-10-21T00:00:00Z",
    etapa1: makeEtapa1Result({ datos, alfa: 0.1 }),
    etapa2: makeEtapa2({ seleccion: SELECCION }),
    serie: datos.serie_efectiva,
    timestamps: datos.timestamps_efectivos,
    configuracion: {
      cramer_particion: { n1_pct: 70, n2_pct: 35 },
      mes_inicio_anio: 7,
      alfa: 0.1,
    },
    decisiones: {},
    ...overrides,
  };
}

function montar(analisis: AnalysisDetail) {
  const fetchMock = stubFetchRouted([
    // DECISIÓN 080 — antes que el GET del detalle, que también contiene "/history/an-1".
    {
      match: (url, init) => init?.method === "POST" && url.includes("/exclusiones"),
      status: 200,
      responder: (_url, init) => {
        const { indices_excluidos } = JSON.parse(String(init?.body));
        return exclusion("ex-nueva", indices_excluidos);
      },
    },
    {
      match: (url, init) => init?.method === "DELETE" && url.includes("/exclusiones/"),
      status: 200,
      body: { ok: true },
    },
    {
      match: (url, init) => init?.method === "POST" && url.includes("/simulate-exclusion"),
      status: 200,
      body: makeSimulacion(),
    },
    { match: (url) => url.includes("/history/an-1"), status: 200, body: analisis },
  ]);
  renderPage(
    <MemoryRouter initialEntries={["/history/an-1"]}>
      <Routes>
        <Route path="/history/:id" element={<HistoryDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
  return { fetchMock, user: userEvent.setup() };
}

async function simularExcluyendo(user: ReturnType<typeof userEvent.setup>, indice: number) {
  const grilla = await screen.findByRole("group", { name: /Años de la serie/ });
  await user.click(within(grilla).getAllByRole("button")[indice]);
  await user.click(screen.getByRole("button", { name: RECALCULAR }));
  await screen.findByText("Resultados sin los puntos excluidos");
}

describe("HistoryDetailPage — what-if de atípicos (bloque B)", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
  });

  it("pide la simulación con la serie, los años, el α, la partición y la elección persistidos", async () => {
    const { fetchMock, user } = montar(detalle());

    await simularExcluyendo(user, 3);

    const datos = makeEtapa1Datos();
    const llamada = fetchMock.mock.calls.find(([url]) => String(url).includes("/simulate-exclusion"));
    expect(JSON.parse(String((llamada![1] as RequestInit).body))).toEqual({
      serie: datos.serie_efectiva,
      anios: datos.timestamps_efectivos!.map((t) => t.anio),
      tipo_variable: "caudal_precipitacion",
      cramer_particion: '{"n1_pct":70,"n2_pct":35}',
      indices_excluidos: [3],
      etapas: [1, 2],
      alfa: 0.1,
      seleccion: { distribucion: "gumbel", metodo: "momentos", periodos_retorno: [2, 10, 100] },
    });
  });

  it("no llama a ningún endpoint que modifique el análisis (DECISIÓN 062)", async () => {
    const { fetchMock, user } = montar(detalle());

    await simularExcluyendo(user, 3);

    const posts = fetchMock.mock.calls
      .filter(([, init]) => (init as RequestInit | undefined)?.method === "POST")
      .map(([url]) => String(url));
    expect(posts).toEqual([expect.stringContaining("/analysis/simulate-exclusion")]);
  });

  it("con una simulación vigente ofrece el PDF con ella", async () => {
    const pdf = { blob: new Blob(["%PDF"]), nombre: "metis_x_simulacion.pdf" };
    obtenerPdfAnalisis.mockResolvedValue(pdf);
    const { user } = montar(detalle());

    expect(
      await screen.findByRole("button", { name: "Exportar PDF" }),
    ).toBeInTheDocument();
    // makeSimulacion() responde con el índice 5 excluido.
    await simularExcluyendo(user, 5);
    await user.click(screen.getByRole("button", { name: "Exportar PDF con la simulación" }));

    expect(obtenerPdfAnalisis).toHaveBeenCalledWith("an-1", [5]);
  });

  it("un análisis anterior a la DECISIÓN 058 (sin timestamps) no ofrece simular y explica por qué", async () => {
    montar(detalle({ timestamps: null }));

    expect(await screen.findByText(/tampoco la simulación sin puntos excluidos/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: RECALCULAR })).not.toBeInTheDocument();
  });

  // ── DECISIÓN 080 — exclusiones guardadas (bloque C2) ──────────────────────

  it("guarda la exclusión de la comparación y la suma a 'Exclusiones guardadas'", async () => {
    const { fetchMock, user } = montar(detalle());

    await simularExcluyendo(user, 3);
    await user.click(screen.getByRole("button", { name: "Guardar esta exclusión en el historial" }));

    const seccion = await screen.findByRole("region", { name: "Exclusiones guardadas" });
    expect(seccion).toHaveTextContent("Sin 2003");
    expect(screen.getByText(/Guardada: esta exclusión figura en el historial/)).toBeInTheDocument();
    const posts = fetchMock.mock.calls
      .filter(([, init]) => (init as RequestInit | undefined)?.method === "POST")
      .map(([url]) => String(url));
    expect(posts).toEqual([
      expect.stringContaining("/analysis/simulate-exclusion"),
      expect.stringContaining("/history/an-1/exclusiones"),
    ]);
  });

  it("'Ver' carga la selección guardada y recalcula la comparación", async () => {
    const { fetchMock, user } = montar(detalle({ exclusiones: [exclusion("ex-1", [3, 7])] }));

    await user.click(await screen.findByRole("button", { name: "Ver la exclusión sin 2003, 2007" }));

    await screen.findByText("Resultados sin los puntos excluidos");
    const llamada = fetchMock.mock.calls.find(([url]) => String(url).includes("/simulate-exclusion"));
    expect(JSON.parse(String((llamada![1] as RequestInit).body)).indices_excluidos).toEqual([3, 7]);
    // Ya está guardada: no se vuelve a ofrecer guardarla.
    expect(
      screen.queryByRole("button", { name: "Guardar esta exclusión en el historial" }),
    ).not.toBeInTheDocument();
  });

  it("'Quitar' la borra del historial", async () => {
    const { fetchMock, user } = montar(detalle({ exclusiones: [exclusion("ex-1", [3, 7])] }));

    await user.click(await screen.findByRole("button", { name: "Quitar la exclusión sin 2003, 2007" }));

    expect(screen.queryByRole("region", { name: "Exclusiones guardadas" })).not.toBeInTheDocument();
    const borrado = fetchMock.mock.calls.find(
      ([, init]) => (init as RequestInit | undefined)?.method === "DELETE",
    );
    expect(String(borrado![0])).toContain("/api/v1/history/an-1/exclusiones/ex-1");
  });
});
