import { afterEach, describe, expect, it, vi } from "vitest";
import { screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "../../auth/AuthProvider";
import { renderPage } from "../../test/renderPage";
import { ConfigPage } from "./ConfigPage";
import { RESIZE_KEYBOARD_STEP } from "./useColumnPanelDock";
import type { AnalysisStreamForm } from "../../api/types";

function StreamProbe() {
  const location = useLocation();
  const form = (location.state as { form?: AnalysisStreamForm } | null)?.form;
  return <pre data-testid="stream-state">{JSON.stringify(form ?? null)}</pre>;
}

// Dos endpoints distintos por detrás de un solo fetch mockeado — necesita
// distinguir por URL (mismo patrón que TopBar.test.tsx). preview por
// defecto en 500: los tests que no le importa el resultado de la
// previsualización (los cuatro heredados de antes de D3) así ejercitan el
// camino de degradación a inputs de texto sin tener que pensarlo — es
// literalmente el comportamiento esperado si preview-columns falla.
function stubFetch({
  me = { ok: false, status: 401, body: {} },
  preview = { ok: false, status: 500, body: {} },
}: {
  me?: { ok: boolean; status?: number; body: unknown };
  preview?: { ok: boolean; status?: number; body: unknown };
} = {}) {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.includes("/auth/me")) {
        return Promise.resolve({
          ok: me.ok,
          status: me.status ?? (me.ok ? 200 : 401),
          json: () => Promise.resolve(me.body),
        });
      }
      if (url.includes("/analysis/preview-columns")) {
        return Promise.resolve({
          ok: preview.ok,
          status: preview.status ?? (preview.ok ? 200 : 500),
          json: () => Promise.resolve(preview.body),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }),
  );
}

function renderConfigPage() {
  return renderPage(
    <MemoryRouter initialEntries={["/config"]}>
      <AuthProvider>
        <Routes>
          <Route path="/config" element={<ConfigPage />} />
          <Route path="/stream" element={<StreamProbe />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

async function waitForReady() {
  expect(
    await screen.findByRole("heading", { name: "Nuevo análisis" }),
  ).toBeInTheDocument();
}

describe("ConfigPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("shows a validation error when submitting without a file", async () => {
    stubFetch();
    renderConfigPage();
    await waitForReady();

    fireEvent.change(screen.getByLabelText("Columna X"), { target: { value: "anio" } });
    fireEvent.change(screen.getByLabelText("Columna Y"), { target: { value: "caudal" } });
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(screen.getByRole("alert")).toHaveTextContent("Seleccioná un archivo");
  });

  it("shows a validation error when the columns are empty", async () => {
    stubFetch();
    renderConfigPage();
    await waitForReady();

    const file = new File(["1,100"], "serie.csv", { type: "text/csv" });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });
    // Deja asentarse el preview fallido (stub por defecto en 500) antes de
    // seguir — si no, la actualización de estado llega después de terminado
    // el test y Testing Library se queja con un warning de act().
    await screen.findByText(/No pudimos leer las columnas/);
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(screen.getByRole("alert")).toHaveTextContent("Completá las dos columnas");
  });

  it("navigates to /stream with the assembled form when authenticated (docencia)", async () => {
    stubFetch({
      me: {
        ok: true,
        body: { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true },
      },
    });
    renderConfigPage();
    await waitForReady();

    const file = new File(["1,100"], "serie.csv", { type: "text/csv" });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });
    fireEvent.change(screen.getByLabelText("Columna X"), { target: { value: "anio" } });
    fireEvent.change(screen.getByLabelText("Columna Y"), { target: { value: "caudal" } });
    fireEvent.click(screen.getByRole("button", { name: "Otro" }));
    fireEvent.click(screen.getByRole("button", { name: "Experto" }));
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(await screen.findByTestId("stream-state")).toBeInTheDocument();
    const form = JSON.parse(screen.getByTestId("stream-state").textContent ?? "null");
    expect(form).toMatchObject({
      columna_x: "anio",
      columna_y: "caudal",
      tipo_variable: "otro",
      modo: "experto",
      cramer_particion: "default",
      mes_inicio_anio: 7,
    });
  });

  it("forces modo=experto and hides the toggle for anonymous sessions", async () => {
    stubFetch();
    renderConfigPage();
    await waitForReady();

    expect(screen.getByText("anónimo · solo resultados")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Paso a paso" })).not.toBeInTheDocument();

    const file = new File(["1,100"], "serie.csv", { type: "text/csv" });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });
    fireEvent.change(screen.getByLabelText("Columna X"), { target: { value: "anio" } });
    fireEvent.change(screen.getByLabelText("Columna Y"), { target: { value: "caudal" } });
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(await screen.findByTestId("stream-state")).toBeInTheDocument();
    const form = JSON.parse(screen.getByTestId("stream-state").textContent ?? "null");
    expect(form.modo).toBe("experto");
  });

  // D3 (plan pasada4 §6) — a partir de acá, los cuatro caminos que el plan
  // pide cubrir explícitamente.

  it("preselects Columna X (fecha/año) and Columna Y (numérica) heurísticamente", async () => {
    stubFetch({
      preview: {
        ok: true,
        body: {
          columnas: [
            { nombre: "anio", indice: 0, muestra: ["1980", "1981", "1982"] },
            { nombre: "caudal", indice: 1, muestra: ["94.71", "89.83", "105.13"] },
          ],
          filas: 40,
        },
      },
    });
    renderConfigPage();
    await waitForReady();

    const file = new File(["anio,caudal\n1980,94.71\n"], "serie.csv", {
      type: "text/csv",
    });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });

    // findByLabelText resolvería de inmediato contra el <input> que ya
    // existe desde "loading" — hace falta el rol específico de <select>
    // (combobox) para esperar de verdad a que preview llegue a "ready".
    const selectX = await screen.findByRole("combobox", { name: "Columna X" });
    expect(selectX.tagName).toBe("SELECT");
    expect(selectX).toHaveValue("0");
    expect(screen.getByLabelText("Columna Y")).toHaveValue("1");
  });

  it("lets the user override the heuristic preselection by hand", async () => {
    stubFetch({
      preview: {
        ok: true,
        body: {
          columnas: [
            { nombre: "anio", indice: 0, muestra: ["1980", "1981", "1982"] },
            { nombre: "caudal", indice: 1, muestra: ["94.71", "89.83", "105.13"] },
            { nombre: "temperatura", indice: 2, muestra: ["18.2", "19.1", "17.5"] },
          ],
          filas: 40,
        },
      },
    });
    renderConfigPage();
    await waitForReady();

    const file = new File(["a"], "serie.csv", { type: "text/csv" });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });

    await screen.findByRole("combobox", { name: "Columna X" });
    // La heurística eligió "caudal" (índice 1) para Y — el usuario prefiere
    // "temperatura" (índice 2) en su lugar.
    fireEvent.change(screen.getByLabelText("Columna Y"), { target: { value: "2" } });

    expect(screen.getByLabelText("Columna Y")).toHaveValue("2");
  });

  it("desambigua nombres de columna duplicados con el índice en la etiqueta", async () => {
    stubFetch({
      preview: {
        ok: true,
        body: {
          columnas: [
            { nombre: "valor", indice: 0, muestra: ["1980", "1981"] },
            { nombre: "valor", indice: 1, muestra: ["94.71", "89.83"] },
          ],
          filas: 40,
        },
      },
    });
    renderConfigPage();
    await waitForReady();

    const file = new File(["a"], "sin-cabecera.csv", { type: "text/csv" });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });

    const selectX = await screen.findByRole("combobox", { name: "Columna X" });
    const options = Array.from(selectX.querySelectorAll("option")).map(
      (o) => o.textContent,
    );
    expect(options).toEqual(
      expect.arrayContaining([
        expect.stringContaining("valor (col. 1)"),
        expect.stringContaining("valor (col. 2)"),
      ]),
    );
  });

  it("degrada a inputs de texto y avisa, sin bloquear el análisis, si la previsualización falla", async () => {
    stubFetch({ preview: { ok: false, status: 500, body: {} } });
    renderConfigPage();
    await waitForReady();

    const file = new File(["a"], "serie.csv", { type: "text/csv" });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });

    await screen.findByText(/No pudimos leer las columnas/);
    const inputX = screen.getByLabelText("Columna X");
    expect(inputX.tagName).toBe("INPUT");

    fireEvent.change(inputX, { target: { value: "anio" } });
    fireEvent.change(screen.getByLabelText("Columna Y"), { target: { value: "caudal" } });
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(await screen.findByTestId("stream-state")).toBeInTheDocument();
  });

  // Bloque E (plan pasada5 §5) — dropzone + panel de muestra de columnas.

  it("soltar un archivo en la dropzone dispara preview-columns y puebla los selects, igual que elegirlo por el input", async () => {
    stubFetch({
      preview: {
        ok: true,
        body: {
          columnas: [
            { nombre: "anio", indice: 0, muestra: ["1980", "1981", "1982"] },
            { nombre: "caudal", indice: 1, muestra: ["94.71", "89.83", "105.13"] },
          ],
          filas: 40,
        },
      },
    });
    renderConfigPage();
    await waitForReady();

    const file = new File(["anio,caudal\n1980,94.71\n"], "serie.csv", {
      type: "text/csv",
    });
    fireEvent.drop(screen.getByTestId("config-dropzone"), {
      dataTransfer: { files: [file] },
    });

    const selectX = await screen.findByRole("combobox", { name: "Columna X" });
    expect(selectX).toHaveValue("0");
    expect(screen.getByLabelText("Columna Y")).toHaveValue("1");
  });

  it("el panel de muestra se puebla; el <option> del select no repite la muestra (P8)", async () => {
    stubFetch({
      preview: {
        ok: true,
        body: {
          columnas: [
            { nombre: "anio", indice: 0, muestra: ["1980", "1981", "1982"] },
            { nombre: "caudal", indice: 1, muestra: ["94.71", "89.83", "105.13"] },
          ],
          filas: 40,
        },
      },
    });
    renderConfigPage();
    await waitForReady();

    const file = new File(["anio,caudal\n1980,94.71\n"], "serie.csv", {
      type: "text/csv",
    });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });

    const selectX = await screen.findByRole("combobox", { name: "Columna X" });
    const optionsText = Array.from(selectX.querySelectorAll("option"))
      .map((o) => o.textContent)
      .join(" ");
    expect(optionsText).not.toContain("94.71");

    expect(screen.getByText("94.71")).toBeInTheDocument();
    expect(screen.getByText("40 filas en el archivo")).toBeInTheDocument();
  });

  it("focus en un select resalta la columna correspondiente en el panel; blur la desresalta", async () => {
    stubFetch({
      preview: {
        ok: true,
        body: {
          columnas: [
            { nombre: "anio", indice: 0, muestra: ["1980", "1981", "1982"] },
            { nombre: "caudal", indice: 1, muestra: ["94.71", "89.83", "105.13"] },
          ],
          filas: 40,
        },
      },
    });
    renderConfigPage();
    await waitForReady();

    const file = new File(["anio,caudal\n1980,94.71\n"], "serie.csv", {
      type: "text/csv",
    });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });

    // La heurística preselecciona "anio" (índice 0) en Columna X.
    const selectX = await screen.findByRole("combobox", { name: "Columna X" });
    const header = screen.getByRole("columnheader", { name: "anio" });
    expect(header).not.toHaveClass("column-preview-panel__col--activa");

    fireEvent.focus(selectX);
    expect(header).toHaveClass("column-preview-panel__col--activa");

    fireEvent.blur(selectX);
    expect(header).not.toHaveClass("column-preview-panel__col--activa");
  });

  // Bloque F5 del plan de Etapa 2 (DECISIÓN 057) — selector de mes de inicio.

  // Sube un CSV cuya columna X ("fecha") tiene la muestra dada — la
  // heurística de preselección elige esa columna por patrón, no por nombre,
  // así que sirve tanto para año puro como para fecha diaria/mensual.
  async function subirColumnaXCon(muestraX: string[]) {
    stubFetch({
      preview: {
        ok: true,
        body: {
          columnas: [
            { nombre: "fecha", indice: 0, muestra: muestraX },
            { nombre: "caudal", indice: 1, muestra: ["94.71", "89.83", "105.13"] },
          ],
          filas: 40,
        },
      },
    });
    renderConfigPage();
    await waitForReady();
    const file = new File(["fecha,caudal\n1980-01-01,94.71\n"], "serie.csv", {
      type: "text/csv",
    });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });
    await screen.findByRole("combobox", { name: "Columna X" });
  }

  it("deshabilita el selector de mes cuando la columna X elegida es un año puro", async () => {
    await subirColumnaXCon(["1980", "1981", "1982"]);

    expect(screen.getByLabelText("Mes de inicio del año")).toBeDisabled();
    expect(screen.getByText(/ya son años/)).toBeInTheDocument();
  });

  it("habilita el selector de mes cuando la columna X elegida es una fecha completa", async () => {
    await subirColumnaXCon(["1980-01-15", "1980-02-15"]);

    expect(screen.getByLabelText("Mes de inicio del año")).toBeEnabled();
  });

  it("manda el mes elegido por el usuario en el form, no solo el default", async () => {
    stubFetch();
    renderConfigPage();
    await waitForReady();

    const file = new File(["1,100"], "serie.csv", { type: "text/csv" });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });
    fireEvent.change(screen.getByLabelText("Columna X"), { target: { value: "anio" } });
    fireEvent.change(screen.getByLabelText("Columna Y"), { target: { value: "caudal" } });
    fireEvent.change(screen.getByLabelText("Mes de inicio del año"), {
      target: { value: "9" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(await screen.findByTestId("stream-state")).toBeInTheDocument();
    const form = JSON.parse(screen.getByTestId("stream-state").textContent ?? "null");
    expect(form.mes_inicio_anio).toBe(9);
  });

  // PR 2.5 (DECISIÓN 065 / R0.2) — selector "pico vs. media" para series diarias.

  it("muestra el selector de tipo de dato diario solo si la columna X parece diaria", async () => {
    await subirColumnaXCon(["1980-01-01", "1980-01-02", "1980-01-03"]);

    expect(screen.getByText("Tipo de dato diario")).toBeInTheDocument();
    expect(
      screen.getByText(/pueden quedar por debajo del pico instantáneo real/),
    ).toBeInTheDocument();
  });

  it("no muestra el selector diario para una columna mensual", async () => {
    await subirColumnaXCon(["1980-01-15", "1980-02-15"]);

    expect(screen.queryByText("Tipo de dato diario")).not.toBeInTheDocument();
  });

  it("manda variable_diaria='media' cuando el usuario elige 'Medias diarias'", async () => {
    await subirColumnaXCon(["1980-01-01", "1980-01-02", "1980-01-03"]);

    fireEvent.click(screen.getByRole("button", { name: "Medias diarias" }));
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    const form = JSON.parse(
      (await screen.findByTestId("stream-state")).textContent ?? "null",
    );
    expect(form.variable_diaria).toBe("media");
  });

  // Bloque E (plan post-avance) — panel de columnas acoplable.

  function stubFetchConPreview() {
    stubFetch({
      preview: {
        ok: true,
        body: {
          columnas: [
            { nombre: "anio", indice: 0, muestra: ["1980", "1981", "1982"] },
            { nombre: "caudal", indice: 1, muestra: ["94.71", "89.83", "105.13"] },
          ],
          filas: 40,
        },
      },
    });
  }

  async function subirArchivoDeMuestra() {
    const file = new File(["anio,caudal\n1980,94.71\n"], "serie.csv", {
      type: "text/csv",
    });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });
    await screen.findByRole("columnheader", { name: "anio" });
  }

  it("E — cierra el panel con el botón × y lo reabre con 'Ver columnas', sin perder las columnas", async () => {
    stubFetchConPreview();
    renderConfigPage();
    await waitForReady();
    await subirArchivoDeMuestra();

    fireEvent.click(screen.getByRole("button", { name: "Cerrar panel de columnas" }));
    expect(screen.queryByRole("columnheader", { name: "anio" })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Ver columnas" }));
    expect(screen.getByRole("columnheader", { name: "anio" })).toBeInTheDocument();
  });

  it("E — elegir una posición de acople marca el botón activo y actualiza data-dock en el shell", async () => {
    stubFetchConPreview();
    const { container } = renderConfigPage();
    await waitForReady();
    await subirArchivoDeMuestra();

    const shell = container.querySelector(".config-shell");
    expect(shell).toHaveAttribute("data-dock", "right");
    expect(screen.getByRole("button", { name: "Derecha" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );

    fireEvent.click(screen.getByRole("button", { name: "Izquierda" }));

    expect(shell).toHaveAttribute("data-dock", "left");
    expect(screen.getByRole("button", { name: "Izquierda" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByRole("button", { name: "Derecha" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
  });

  it("E — persiste posición de acople y abierto/cerrado en localStorage (metis-column-panel)", async () => {
    stubFetchConPreview();
    renderConfigPage();
    await waitForReady();
    await subirArchivoDeMuestra();

    fireEvent.click(screen.getByRole("button", { name: "Abajo" }));
    fireEvent.click(screen.getByRole("button", { name: "Cerrar panel de columnas" }));

    const stored = JSON.parse(localStorage.getItem("metis-column-panel") ?? "null");
    expect(stored).toMatchObject({ dock: "bottom", open: false });
  });

  it("E — el divisor responde a las flechas del teclado y actualiza aria-valuenow", async () => {
    stubFetchConPreview();
    renderConfigPage();
    await waitForReady();
    await subirArchivoDeMuestra();

    const divisor = screen.getByRole("separator", {
      name: "Redimensionar panel de columnas",
    });
    const inicial = Number(divisor.getAttribute("aria-valuenow"));

    // dock="right" (default): ArrowLeft aleja el divisor del panel — el
    // panel crece.
    fireEvent.keyDown(divisor, { key: "ArrowLeft" });
    expect(Number(divisor.getAttribute("aria-valuenow"))).toBe(inicial + RESIZE_KEYBOARD_STEP);

    fireEvent.keyDown(divisor, { key: "ArrowRight" });
    expect(Number(divisor.getAttribute("aria-valuenow"))).toBe(inicial);
  });

  it("E — no muestra el divisor ni el panel cuando no hay preview lista", async () => {
    stubFetch(); // default: preview en 500 → nunca llega a "ready"
    renderConfigPage();
    await waitForReady();

    expect(screen.queryByRole("separator")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Ver columnas" })).not.toBeInTheDocument();
  });

  // Bloque F (plan post-avance, Opción 1) — nota explicando qué hace
  // realmente "Tipo de variable".

  it("F — explica qué cambia el toggle de tipo de variable", async () => {
    stubFetch();
    renderConfigPage();
    await waitForReady();

    expect(
      screen.getByText(/METIS avisa si hay valores negativos/),
    ).toBeInTheDocument();
    expect(screen.getByText(/trata los ceros de forma distinta en la prueba de Chow/)).toBeInTheDocument();
  });

  // Bloque H1 (plan post-avance, DECISIÓN 036) — partición de Cramer personalizada.

  async function llenarCamposMinimos() {
    const file = new File(["1,100"], "serie.csv", { type: "text/csv" });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });
    // Deja asentarse el preview fallido (stub por defecto en 500) antes de
    // seguir — mismo motivo que el resto de los tests de este archivo.
    await screen.findByText(/No pudimos leer las columnas/);
    fireEvent.change(screen.getByLabelText("Columna X"), { target: { value: "anio" } });
    fireEvent.change(screen.getByLabelText("Columna Y"), { target: { value: "caudal" } });
  }

  it("H1 — 'Personalizada' muestra dos campos con los defaults 60/30 visibles", async () => {
    stubFetch();
    renderConfigPage();
    await waitForReady();

    expect(screen.queryByLabelText("% período largo")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Personalizada" }));

    expect(screen.getByLabelText("% período largo")).toHaveValue("60");
    expect(screen.getByLabelText("% período corto")).toHaveValue("30");
  });

  it("H1 — manda la partición personalizada como objeto en el form", async () => {
    stubFetch();
    renderConfigPage();
    await waitForReady();
    await llenarCamposMinimos();

    fireEvent.click(screen.getByRole("button", { name: "Personalizada" }));
    fireEvent.change(screen.getByLabelText("% período largo"), { target: { value: "70" } });
    fireEvent.change(screen.getByLabelText("% período corto"), { target: { value: "20" } });
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(await screen.findByTestId("stream-state")).toBeInTheDocument();
    const form = JSON.parse(screen.getByTestId("stream-state").textContent ?? "null");
    expect(form.cramer_particion).toEqual({ n1_pct: 70, n2_pct: 20 });
  });

  it("H1 — rechaza n1_pct ≤ n2_pct con un error inline, sin navegar", async () => {
    stubFetch();
    renderConfigPage();
    await waitForReady();
    await llenarCamposMinimos();

    fireEvent.click(screen.getByRole("button", { name: "Personalizada" }));
    fireEvent.change(screen.getByLabelText("% período largo"), { target: { value: "20" } });
    fireEvent.change(screen.getByLabelText("% período corto"), { target: { value: "60" } });
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(screen.getByRole("alert")).toHaveTextContent(/período largo/);
    expect(screen.queryByTestId("stream-state")).not.toBeInTheDocument();
  });

  it("H1 — rechaza un porcentaje fuera de [1, 100] con un error inline", async () => {
    stubFetch();
    renderConfigPage();
    await waitForReady();
    await llenarCamposMinimos();

    fireEvent.click(screen.getByRole("button", { name: "Personalizada" }));
    fireEvent.change(screen.getByLabelText("% período largo"), { target: { value: "150" } });
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(screen.getByRole("alert")).toHaveTextContent(/entre 1 y 100/);
    expect(screen.queryByTestId("stream-state")).not.toBeInTheDocument();
  });

  it("H1 — volver a 'Default 60/30' manda 'default' de nuevo, no el último valor personalizado", async () => {
    stubFetch();
    renderConfigPage();
    await waitForReady();
    await llenarCamposMinimos();

    fireEvent.click(screen.getByRole("button", { name: "Personalizada" }));
    fireEvent.change(screen.getByLabelText("% período largo"), { target: { value: "70" } });
    fireEvent.click(screen.getByRole("button", { name: "Default 60/30" }));
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(await screen.findByTestId("stream-state")).toBeInTheDocument();
    const form = JSON.parse(screen.getByTestId("stream-state").textContent ?? "null");
    expect(form.cramer_particion).toBe("default");
  });
});
