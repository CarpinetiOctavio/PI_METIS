import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "../../auth/AuthProvider";
import { ConfigPage } from "./ConfigPage";
import type { AnalysisStreamForm } from "../../api/types";

function StreamProbe() {
  const location = useLocation();
  const form = (location.state as { form?: AnalysisStreamForm } | null)?.form;
  return <pre data-testid="stream-state">{JSON.stringify(form ?? null)}</pre>;
}

function stubMe(ok: boolean, body: unknown = {}) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      status: ok ? 200 : 401,
      json: () => Promise.resolve(body),
    }),
  );
}

function renderConfigPage() {
  return render(
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
    stubMe(false);
    renderConfigPage();
    await waitForReady();

    fireEvent.change(screen.getByLabelText("Columna X"), { target: { value: "anio" } });
    fireEvent.change(screen.getByLabelText("Columna Y"), { target: { value: "caudal" } });
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(screen.getByRole("alert")).toHaveTextContent("Seleccioná un archivo");
  });

  it("shows a validation error when the columns are empty", async () => {
    stubMe(false);
    renderConfigPage();
    await waitForReady();

    const file = new File(["1,100"], "serie.csv", { type: "text/csv" });
    fireEvent.change(screen.getByLabelText("Archivo (CSV o Excel)"), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Ejecutar análisis/ }));

    expect(screen.getByRole("alert")).toHaveTextContent("Completá las dos columnas");
  });

  it("navigates to /stream with the assembled form when authenticated (docencia)", async () => {
    stubMe(true, { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true });
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
    });
  });

  it("forces modo=experto and hides the toggle for anonymous sessions", async () => {
    stubMe(false);
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
});
