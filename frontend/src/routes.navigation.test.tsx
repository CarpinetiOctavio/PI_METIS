// Capa 2 de testing (docs/frontend/plan-arreglo-ui-rota.md §4.2-b): el grafo
// de navegación REAL — `routes` tal cual lo consume App.tsx, no un
// MemoryRouter con destinos de mentira armados por cada test aislado. Con el
// patrón anterior (cada archivo de página con su propio <Routes> falso),
// "¿existe algún camino de clicks que lleve a /history?" no se podía ni
// formular. Este archivo cubre F4, F5, F6 y F7 de una sola pasada, más el
// camino feliz de login (§5.3 del informe) — el de mejor relación
// costo/beneficio de todo el plan.
import { afterEach, describe, expect, it, vi } from "vitest";
import { act, screen, fireEvent } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { routes } from "./routes";
import { AuthProvider } from "./auth/AuthProvider";
import { ThemeProvider } from "./theme/ThemeProvider";
import { renderPage } from "./test/renderPage";
import { designEventsMock } from "./mocks/designEvents.mock";
import type { AnalysisDetail } from "./api/types";

vi.mock("@microsoft/fetch-event-source", () => ({
  fetchEventSource: vi.fn(),
}));

const mockedFetchEventSource = vi.mocked(fetchEventSource);

function lastStreamOptions() {
  const call = mockedFetchEventSource.mock.calls.at(-1);
  if (!call) throw new Error("fetchEventSource no fue llamado todavía");
  return call[1];
}

function emitStream(type: string, payload: Record<string, unknown> = {}) {
  act(() => {
    lastStreamOptions().onmessage?.({ event: type, data: JSON.stringify(payload), id: "" } as never);
  });
}

const TODOS_LOS_GRUPOS = [
  "anderson",
  "wald_wolfowitz",
  "helmert",
  "t_student",
  "cramer",
  "mann_kendall",
  "kolmogorov_smirnov",
  "chow",
];

function completeStream() {
  TODOS_LOS_GRUPOS.forEach((prueba) =>
    emitStream("test_result", {
      prueba,
      estadistico: 0.5,
      valor_critico: 1,
      veredicto: "aprobada",
      warning_codigo: null,
      warning_nivel: null,
      n1: null,
      n2: null,
      valor_atipico: null,
      iteracion: 1,
    }),
  );
  emitStream("result_etapa1", {
    contract: { bloqueante: false, codigo_error: null, warnings: [] },
    descriptive: null,
    independencia: [],
    homogeneidad: [],
    tendencia: [],
    atipicos: [],
    nivel_independencia: "independiente",
    nivel_homogeneidad: "homogeneidad_ok",
    nivel_confianza: "validado",
    warnings: [],
  });
  emitStream("complete", { analysis_id: "an-1" });
}

function makeAnalysisDetail(): AnalysisDetail {
  return {
    id: "an-1",
    tipo_variable: "caudal_precipitacion",
    modo: "experto",
    etapas: ["1"],
    created_at: "2026-01-15T00:00:00Z",
    etapa1: {
      contract: { bloqueante: false, codigo_error: null, warnings: [] },
      descriptive: null,
      independencia: [],
      homogeneidad: [],
      tendencia: [],
      atipicos: [],
      nivel_independencia: "independiente",
      nivel_homogeneidad: "homogeneidad_ok",
      nivel_confianza: "validado",
      warnings: [],
    },
    etapa2: null,
  };
}

// `authed` controla el estado de sesión de ARRANQUE (para el escenario
// anónimo/sin-sesión). El escenario autenticado necesita algo distinto: la
// puerta de entrada solo muestra el formulario de login si /auth/me NO
// confirma sesión todavía — así que ese escenario arranca sin sesión y
// recién after POST /auth/login empieza a devolver el usuario, igual que el
// patrón ya usado en AuthProvider.test.tsx ("login() calls /login then
// refetches /me").
function stubFetch({ authed }: { authed: boolean }) {
  const user = { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true };
  let loggedIn = authed;

  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input.toString();
      const json = (body: unknown, ok = true, status = ok ? 200 : 400) =>
        Promise.resolve({ ok, status, json: () => Promise.resolve(body) });

      if (url.includes("/auth/me")) {
        return json(loggedIn ? user : {}, loggedIn, loggedIn ? 200 : 401);
      }
      if (url.includes("/auth/login")) {
        loggedIn = true;
        return json({ ok: true });
      }
      if (url.includes("/auth/logout")) {
        loggedIn = false;
        return json({ ok: true });
      }
      if (url.includes("/analysis/design-events")) return json(designEventsMock);
      if (/\/history\/[^/]+$/.test(url)) return json(makeAnalysisDetail());
      if (url.includes("/history/")) {
        return json([
          {
            id: "an-1",
            tipo_variable: "caudal_precipitacion",
            modo: "experto",
            etapas: ["1"],
            created_at: "2026-01-15T00:00:00Z",
          },
        ]);
      }
      throw new Error(`unstubbed fetch: ${url}`);
    }),
  );
}

function makeCsvFile() {
  return new File(["anio,caudal\n1980,100"], "serie.csv", { type: "text/csv" });
}

function renderApp(initialPath: string) {
  // Misma composición real que main.tsx: ThemeProvider por fuera de
  // AuthProvider/Router — TopBar (dentro de RootLayout) necesita ambos
  // contextos, y App.tsx en sí no incluye ThemeProvider (lo agrega main.tsx).
  const router = createMemoryRouter(routes, { initialEntries: [initialPath] });
  return renderPage(
    <ThemeProvider>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </ThemeProvider>,
  );
}

describe("grafo de navegación real (routes.tsx)", () => {
  afterEach(() => vi.unstubAllGlobals());

  // F4/F5/F6/F7 (anónimo, CU-02): la puerta de entrada, todo el pipeline de
  // Etapa 1, y la continuación mock a Etapa 2 — con un solo click cada paso.
  it("anónimo: entrada -> config -> stream -> resultados -> ranking -> eventos de diseño", async () => {
    stubFetch({ authed: false });
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    renderApp("/");

    fireEvent.click(
      await screen.findByRole("button", { name: /Entrar como anónimo/ }),
    );

    expect(
      await screen.findByRole("heading", { name: "Nuevo análisis" }),
    ).toBeInTheDocument();

    const fileInput = screen.getByLabelText("Archivo (CSV o Excel)");
    fireEvent.change(fileInput, { target: { files: [makeCsvFile()] } });
    fireEvent.change(screen.getByLabelText("Columna X"), { target: { value: "anio" } });
    fireEvent.change(screen.getByLabelText("Columna Y"), { target: { value: "caudal" } });
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(
      await screen.findByRole("heading", { name: "Análisis en vivo" }),
    ).toBeInTheDocument();

    completeStream();
    fireEvent.click(await screen.findByRole("button", { name: /Ver resultados/ }));

    expect(
      await screen.findByRole("heading", { name: "Resultados de Etapa 1" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Continuar a Etapa 2 ▸" }));

    expect(
      await screen.findByRole("heading", { name: "Mejores ajustes" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getAllByRole("button", { name: "Elegir" })[0]);

    expect(
      await screen.findByRole("heading", { name: "Evento de diseño" }),
    ).toBeInTheDocument();
  });

  // F4/F6 + login exitoso (§5.3 del informe: no existía ningún test de este
  // camino porque RedirectIfAuthed vive en routes.tsx, fuera del alcance de
  // EntryPage.test.tsx con sus rutas de mentira).
  it("autenticado: login -> config; Historial -> detalle; Cerrar sesión -> entrada", async () => {
    stubFetch({ authed: false });
    renderApp("/");

    fireEvent.change(
      await screen.findByLabelText("Email institucional"),
      { target: { value: "a@ucc.edu.ar" } },
    );
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "test1234" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ingresar" }));

    expect(
      await screen.findByRole("heading", { name: "Nuevo análisis" }),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("link", { name: "Historial" }));
    expect(
      await screen.findByRole("heading", { name: "Tu historial" }),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByText("caudal_precipitacion"));
    expect(
      await screen.findByRole("heading", { name: "Detalle del análisis" }),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Cerrar sesión" }));
    expect(
      await screen.findByRole("heading", { name: "Puerta de entrada" }),
    ).toBeInTheDocument();
  });

  // F7: sin sesión de ningún tipo, /config no se puede alcanzar navegando
  // directo — antes era exactamente lo que pasaba (F4/F5 lo describen desde
  // el lado de "no hay ningún link"; esto confirma que tampoco alcanza con
  // la URL directa).
  it("sin sesión: navegar directo a /config redirige a la puerta de entrada", async () => {
    stubFetch({ authed: false });
    renderApp("/config");

    expect(
      await screen.findByRole("heading", { name: "Puerta de entrada" }),
    ).toBeInTheDocument();
  });
});
