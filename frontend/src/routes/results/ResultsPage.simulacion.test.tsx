import { afterEach, describe, expect, it, vi } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "../../auth/AuthProvider";
import { renderPage } from "../../test/renderPage";
import { makeEtapa1Datos } from "../../test/etapa1Fixtures";
import { makeEtapa2 } from "../../test/etapa2Fixtures";
import { makeEtapa1Result, makeSimulacion } from "../../test/simulacionFixtures";
import { stubFetchRouted } from "../../test/fetchStubs";
import { formatNum } from "../../i18n/format";
import type { Etapa2EventosState } from "../../api/sse";
import type {
  CramerParticion,
  SimulateExclusionResponse,
  TipoVariable,
} from "../../api/types";
import { ResultsPage } from "./ResultsPage";

// Exportar PDF (DECISIÓN 075): jsdom no implementa URL.createObjectURL, así que
// pedir y guardar el PDF se reemplazan en el borde.
const { obtenerPdfAnalisis, guardarPdf } = vi.hoisted(() => ({
  obtenerPdfAnalisis: vi.fn(),
  guardarPdf: vi.fn(),
}));
vi.mock("../../api/export", () => ({ obtenerPdfAnalisis, guardarPdf }));

// Cableado del what-if de atípicos en la página (ítem A, A2): cuándo aparece el
// botón y qué pide al backend (POST /analysis/simulate-exclusion, DECISIÓN 071).
const RECALCULAR = /Recalcular sin los puntos seleccionados/;

interface Estado {
  tipoVariable?: TipoVariable;
  cramerParticion?: CramerParticion;
  etapas?: "1" | "1,2";
  eventosDiseno?: Etapa2EventosState;
}

function montar(
  estado: Estado = { tipoVariable: "otro" },
  respuesta: SimulateExclusionResponse = makeSimulacion(),
  sesion: { analysisId: string } | null = null,
) {
  const fetchMock = stubFetchRouted([
    {
      match: (url) => url.includes("/auth/me"),
      status: sesion ? 200 : 401,
      body: sesion ? { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true } : {},
    },
    {
      match: (url, init) => init?.method === "POST" && url.includes("/simulate-exclusion"),
      status: 200,
      body: respuesta,
    },
  ]);
  renderPage(
    <MemoryRouter
      initialEntries={[
        {
          pathname: "/results",
          state: {
            result: makeEtapa1Result({ datos: makeEtapa1Datos() }),
            analysisId: sesion?.analysisId ?? null,
            ...estado,
          },
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
    vi.clearAllMocks();
  });

  it("CU-01 — con una simulación vigente ofrece exportar el PDF con ella", async () => {
    const pdf = { blob: new Blob(["%PDF"]), nombre: "metis_x_simulacion.pdf" };
    obtenerPdfAnalisis.mockResolvedValue(pdf);
    const { user } = montar({ tipoVariable: "otro" }, makeSimulacion(), { analysisId: "an-1" });

    // La sesión se confirma con /auth/me después de montar: bajo la carga de la
    // suite completa eso puede pasar el segundo de espera por defecto.
    await screen.findByRole("button", { name: "Exportar PDF" }, { timeout: 5000 });
    expect(
      screen.queryByRole("button", { name: "Exportar PDF con la simulación" }),
    ).not.toBeInTheDocument();

    // makeSimulacion() responde con el año 2005 (índice 5) excluido; el botón
    // usa los índices de la simulación vigente, no la selección en curso.
    const grilla = await screen.findByRole("group", { name: /Años de la serie/ });
    await user.click(within(grilla).getAllByRole("button")[5]);
    await user.click(screen.getByRole("button", { name: RECALCULAR }));
    await screen.findByText("Resultados sin los puntos excluidos");

    await user.click(screen.getByRole("button", { name: "Exportar PDF con la simulación" }));
    expect(obtenerPdfAnalisis).toHaveBeenCalledWith("an-1", [5]);
    expect(guardarPdf).toHaveBeenCalledWith(pdf);
  });

  it("sin la configuración del análisis en el estado tampoco lo ofrece", async () => {
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
    const { fetchMock, user } = montar(estado);

    const grilla = await screen.findByRole("group", { name: /Años de la serie/ });
    const casillas = within(grilla).getAllByRole("button");
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

  describe("eventos de diseño sin los puntos excluidos", () => {
    const ELECCION: Etapa2EventosState = {
      distribucion: "gumbel",
      metodo: "momentos",
      eventos_diseno: [{ periodo_retorno: 100, valor: 312.7 }],
      curva_ajuste: [{ periodo_retorno: 100, valor: 312.7 }],
    };
    const SIMULADA = {
      distribucion: "gumbel",
      metodo: "momentos",
      periodos_retorno: [100],
      eventos_diseno: [{ periodo_retorno: 100, valor: 250.1 }],
      curva_ajuste: [{ periodo_retorno: 100, valor: 250.1 }],
    };
    const conEtapa2 = makeSimulacion({
      etapa2: { ranking: [], warnings: [], puntos_empiricos: [], seleccion: SIMULADA },
    });

    async function recalcular(user: ReturnType<typeof userEvent.setup>) {
      const grilla = await screen.findByRole("group", { name: /Años de la serie/ });
      await user.click(within(grilla).getAllByRole("button")[5]);
      await user.click(screen.getByRole("button", { name: RECALCULAR }));
      await screen.findByText("Resultados sin los puntos excluidos");
    }

    it("manda la elección del stream para que el backend recalcule sus eventos", async () => {
      const { fetchMock, user } = montar(
        { tipoVariable: "otro", etapas: "1,2", eventosDiseno: ELECCION },
        conEtapa2,
      );
      await recalcular(user);

      expect(pedidoDeSimulacion(fetchMock).seleccion).toEqual({
        distribucion: "gumbel",
        metodo: "momentos",
        periodos_retorno: [100],
      });
    });

    it("pasa a la versión recalculada y deja volver a la original", async () => {
      const { user } = montar(
        { tipoVariable: "otro", etapas: "1,2", eventosDiseno: ELECCION },
        conEtapa2,
      );
      expect(screen.getByText(formatNum(312.7))).toBeInTheDocument();
      await recalcular(user);

      const sinExcluidos = screen.getByRole("button", { name: "Sin los puntos excluidos" });
      expect(sinExcluidos).toHaveAttribute("aria-pressed", "true");
      expect(screen.getByText(/reajustada sin 2005/)).toBeInTheDocument();
      expect(screen.getByText(formatNum(250.1))).toBeInTheDocument();

      await user.click(screen.getByRole("button", { name: "Original" }));
      expect(screen.getByText(formatNum(312.7))).toBeInTheDocument();
      expect(screen.queryByText(formatNum(250.1))).not.toBeInTheDocument();
    });

    it("si la elección deja de ajustar sin esos puntos, explica por qué", async () => {
      const { user } = montar(
        { tipoVariable: "otro", etapas: "1,2", eventosDiseno: ELECCION },
        makeSimulacion({
          etapa2: {
            ranking: [],
            warnings: [],
            puntos_empiricos: [],
            seleccion: {
              ...SIMULADA,
              eventos_diseno: [{ periodo_retorno: 100, valor: null }],
              curva_ajuste: [],
              estado: "no_converge",
            },
          },
        }),
      );
      await recalcular(user);

      expect(
        screen.getByText(/Sin los años 2005, gumbel · momentos no se puede ajustar \(no converge\)/),
      ).toBeInTheDocument();
      await user.click(screen.getByRole("button", { name: "Original" }));
      expect(screen.getByText(formatNum(312.7))).toBeInTheDocument();
    });

    it("si sin esos puntos no hay Etapa 2, lo dice y deja los eventos originales", async () => {
      const { user } = montar(
        { tipoVariable: "otro", etapas: "1,2", eventosDiseno: ELECCION },
        makeSimulacion({ etapa2: null }),
      );
      await recalcular(user);

      expect(screen.getByText(/no hay Etapa 2 que recalcular/)).toBeInTheDocument();
      expect(screen.queryByRole("button", { name: "Sin los puntos excluidos" })).not.toBeInTheDocument();
      expect(screen.getByText(formatNum(312.7))).toBeInTheDocument();
    });
  });
});

// Revisión de DECISIÓN 071 (18/10/2026): la exploración de otra distribución
// respeta la simulación de exclusión, con un único selector para las dos columnas.
describe("ResultsPage — exploración con la simulación de exclusión (CU-01)", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
  });

  const ELECCION: Etapa2EventosState = {
    distribucion: "gumbel",
    metodo: "momentos",
    eventos_diseno: [{ periodo_retorno: 100, valor: 312.7 }],
    curva_ajuste: [{ periodo_retorno: 100, valor: 312.7 }],
  };

  // La respuesta del backend depende del pedido: los años excluidos salen de los
  // índices, y `seleccion` repite la combinación pedida con un valor propio.
  function respuestaSimulada(init?: RequestInit): SimulateExclusionResponse {
    const pedido = JSON.parse(String(init?.body));
    const indices: number[] = pedido.indices_excluidos;
    const sel = pedido.seleccion;
    return makeSimulacion({
      excluidos: indices.map((i) => ({ indice: i, periodo: 2000 + i, valor_original: 100 })),
      etapa2: {
        ranking: [],
        warnings: [],
        puntos_empiricos: [],
        seleccion: sel && {
          ...sel,
          eventos_diseno: [{ periodo_retorno: 100, valor: sel.distribucion === "gve" ? 222.2 : 250.1 }],
          curva_ajuste: [],
          estado: "ok",
        },
      },
    });
  }

  function montarExplorable() {
    const fetchMock = stubFetchRouted([
      {
        match: (url) => url.includes("/auth/me"),
        status: 200,
        body: { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true },
      },
      {
        match: (url, init) => init?.method === "POST" && url.includes("/simulate-exclusion"),
        status: 200,
        responder: (_url, init) => respuestaSimulada(init),
      },
      {
        match: (url, init) => init?.method === "POST" && url.includes("/design-events"),
        status: 200,
        body: { eventos_diseno: [{ periodo_retorno: 100, valor: 333.3 }], curva_ajuste: [] },
      },
    ]);
    renderPage(
      <MemoryRouter
        initialEntries={[
          {
            pathname: "/results",
            state: {
              result: makeEtapa1Result({ datos: makeEtapa1Datos() }),
              analysisId: "an-1",
              tipoVariable: "otro",
              etapas: "1,2",
              eventosDiseno: ELECCION,
              etapa2: { session_id: "s", ...makeEtapa2() },
            },
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

  async function simularSin(user: ReturnType<typeof userEvent.setup>, posiciones: number[]) {
    const grilla = await screen.findByRole("group", { name: /Años de la serie/ });
    for (const p of posiciones) await user.click(within(grilla).getAllByRole("button")[p]);
    await user.click(screen.getByRole("button", { name: RECALCULAR }));
  }

  const pedidosSimulados = (fetchMock: ReturnType<typeof stubFetchRouted>) =>
    fetchMock.mock.calls
      .filter(([url]) => String(url).includes("/simulate-exclusion"))
      .map(([, init]) => JSON.parse(String((init as RequestInit).body)));

  async function explorarGve(user: ReturnType<typeof userEvent.setup>) {
    // "gve" es la segunda card del ranking (makeEtapa2).
    await user.click(
      (await screen.findAllByRole("button", { name: "Explorar este ajuste" }, { timeout: 5000 }))[1],
    );
  }

  it("un solo selector cambia a la vez la elección y la exploración", async () => {
    const { fetchMock, user } = montarExplorable();
    await simularSin(user, [5]);
    await screen.findByText(/reajustada sin 2005/);
    await explorarGve(user);

    expect(await screen.findByText(/Exploración sin los años 2005/)).toBeInTheDocument();
    expect(screen.getAllByRole("group", { name: "Ver resultados" })).toHaveLength(1);
    expect(screen.getByText(formatNum(250.1))).toBeInTheDocument();
    expect(screen.getByText(formatNum(222.2))).toBeInTheDocument();
    // La exploración simulada se pide con los mismos puntos y la combinación explorada.
    expect(pedidosSimulados(fetchMock).at(-1)).toMatchObject({
      indices_excluidos: [5],
      seleccion: { distribucion: "gve", metodo: "ml" },
    });

    await user.click(screen.getByRole("button", { name: "Original" }));
    expect(screen.getByText(formatNum(312.7))).toBeInTheDocument();
    expect(screen.getByText(formatNum(333.3))).toBeInTheDocument();
    expect(screen.queryByText(formatNum(222.2))).not.toBeInTheDocument();
    expect(screen.queryByText(formatNum(250.1))).not.toBeInTheDocument();
  });

  it("cambiar la simulación vuelve a pedir la exploración con los puntos nuevos", async () => {
    const { fetchMock, user } = montarExplorable();
    await simularSin(user, [5]);
    await screen.findByText(/reajustada sin 2005/);
    await explorarGve(user);
    await screen.findByText(/Exploración sin los años 2005/);

    await simularSin(user, [7]);

    expect(await screen.findByText(/Exploración sin los años 2005, 2007/)).toBeInTheDocument();
    expect(screen.queryByText(/Exploración sin los años 2005:/)).not.toBeInTheDocument();
    expect(pedidosSimulados(fetchMock).at(-1)).toMatchObject({
      indices_excluidos: [5, 7],
      seleccion: { distribucion: "gve" },
    });
  });

  it("limpiar la simulación oculta el selector y deja la exploración original", async () => {
    const { user } = montarExplorable();
    await simularSin(user, [5]);
    await screen.findByText(/reajustada sin 2005/);
    await explorarGve(user);
    await screen.findByText(/Exploración sin los años 2005/);

    await user.click(screen.getByRole("button", { name: "Limpiar selección" }));

    expect(screen.queryByRole("group", { name: "Ver resultados" })).not.toBeInTheDocument();
    expect(await screen.findByText(formatNum(333.3))).toBeInTheDocument();
    expect(screen.queryByText(/Exploración sin los años/)).not.toBeInTheDocument();
  });
});
