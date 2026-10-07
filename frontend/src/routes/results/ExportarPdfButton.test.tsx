import { afterEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderPage } from "../../test/renderPage";
import { ApiError } from "../../api/client";
import { ExportarPdfButton } from "./ExportarPdfButton";

const { obtenerPdfAnalisis, guardarPdf } = vi.hoisted(() => ({
  obtenerPdfAnalisis: vi.fn(),
  guardarPdf: vi.fn(),
}));

vi.mock("../../api/export", () => ({ obtenerPdfAnalisis, guardarPdf }));

describe("ExportarPdfButton", () => {
  afterEach(() => vi.clearAllMocks());

  it("pide el PDF del análisis y lo guarda", async () => {
    const user = userEvent.setup();
    const pdf = { blob: new Blob(["%PDF"]), nombre: "metis_x.pdf" };
    obtenerPdfAnalisis.mockResolvedValue(pdf);
    renderPage(<ExportarPdfButton analysisId="an-1" />);

    await user.click(screen.getByRole("button", { name: "Exportar PDF" }));

    expect(obtenerPdfAnalisis).toHaveBeenCalledWith("an-1", undefined);
    expect(guardarPdf).toHaveBeenCalledWith(pdf);
    expect(screen.getByRole("button", { name: "Exportar PDF" })).toBeEnabled();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("sin puntos excluidos no ofrece exportar la simulación", () => {
    renderPage(<ExportarPdfButton analysisId="an-1" indicesExcluidos={[]} />);
    expect(
      screen.queryByRole("button", { name: "Exportar PDF con la simulación" }),
    ).not.toBeInTheDocument();
  });

  it("con puntos excluidos exporta también la simulación", async () => {
    const user = userEvent.setup();
    obtenerPdfAnalisis.mockResolvedValue({ blob: new Blob(), nombre: "x.pdf" });
    renderPage(<ExportarPdfButton analysisId="an-1" indicesExcluidos={[3, 17]} />);

    await user.click(screen.getByRole("button", { name: "Exportar PDF con la simulación" }));

    expect(obtenerPdfAnalisis).toHaveBeenCalledWith("an-1", [3, 17]);
    expect(guardarPdf).toHaveBeenCalled();
  });

  it("deshabilita el botón mientras se genera", async () => {
    const user = userEvent.setup();
    let resolver!: (v: { blob: Blob; nombre: string }) => void;
    obtenerPdfAnalisis.mockReturnValue(new Promise((r) => (resolver = r)));
    renderPage(<ExportarPdfButton analysisId="an-1" />);

    await user.click(screen.getByRole("button", { name: "Exportar PDF" }));

    expect(screen.getByRole("button", { name: "Generando PDF…" })).toBeDisabled();
    resolver({ blob: new Blob(), nombre: "x.pdf" });
    expect(await screen.findByRole("button", { name: "Exportar PDF" })).toBeEnabled();
  });

  it("muestra el error traducido si el backend responde con un código", async () => {
    const user = userEvent.setup();
    obtenerPdfAnalisis.mockRejectedValue(
      new ApiError(404, "ANALYSIS_NOT_FOUND", "No existe."),
    );
    renderPage(<ExportarPdfButton analysisId="an-x" />);

    await user.click(screen.getByRole("button", { name: "Exportar PDF" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No se pudo exportar el PDF: El análisis no existe, no te pertenece",
    );
    expect(guardarPdf).not.toHaveBeenCalled();
  });
});
