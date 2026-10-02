import { afterEach, describe, expect, it, vi } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "../../auth/AuthProvider";
import { renderPage } from "../../test/renderPage";
import { makeEtapa1Datos } from "../../test/etapa1Fixtures";
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
) {
  const fetchMock = stubFetchRouted([
    { match: (url) => url.includes("/auth/me"), status: 401, body: {} },
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
