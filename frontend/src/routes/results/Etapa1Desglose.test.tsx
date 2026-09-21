import { describe, expect, it } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { Etapa1Desglose } from "./Etapa1Desglose";
import type { TestResultDetail } from "../../api/types";
import {
  makeAndersonConDesglose,
  makeChowConDesglose,
  makeTestResult,
} from "../../test/etapa1Fixtures";

function conDesglose(base: TestResultDetail, desglose: unknown): TestResultDetail {
  return {
    ...base,
    explicacion: { ...base.explicacion!, desglose: desglose as never },
  };
}

// El desglose todavía no lo emite el backend (Tanda 2): en producción hoy llega
// ausente, y el componente tiene que dejar la pantalla como estaba.
describe("Etapa1Desglose — degradación", () => {
  it.each([
    ["sin explicación", makeTestResult({ prueba: "anderson", explicacion: null })],
    ["desglose ausente", { ...makeAndersonConDesglose(), explicacion: { ecuacion: "III-1", terminos: {} } }],
    ["desglose null", conDesglose(makeAndersonConDesglose(), null)],
    ["desglose vacío", conDesglose(makeAndersonConDesglose(), [])],
    ["prueba sin desglose definido", conDesglose({ ...makeAndersonConDesglose(), prueba: "helmert" }, [{ i: 1 }])],
  ])("no renderiza nada: %s", (_caso, test) => {
    const { container } = render(<Etapa1Desglose test={test} />);
    expect(container).toBeEmptyDOMElement();
  });
});

describe("Etapa1Desglose — Anderson", () => {
  it("muestra el correlograma con una barra por lag y separa los que salen de las bandas", () => {
    const { container } = render(<Etapa1Desglose test={makeAndersonConDesglose()} />);

    expect(screen.getByRole("img", { name: /Correlograma de Anderson/ })).toBeInTheDocument();
    expect(container.querySelectorAll("line.interactive-chart__stem")).toHaveLength(6);
    expect(container.querySelectorAll('[data-series="fuera"] circle')).toHaveLength(1);
    expect(container.querySelectorAll('[data-series="dentro"] circle')).toHaveLength(5);
    // Las bandas del 95% son dos líneas punteadas.
    expect(container.querySelectorAll('path[data-series^="banda-"]')).toHaveLength(2);
  });

  it("la tabla tiene un renglón por lag, marca el que da el estadístico y el que sale de banda", () => {
    render(<Etapa1Desglose test={makeAndersonConDesglose()} />);

    const filas = within(screen.getByRole("table")).getAllByRole("row").slice(1);
    expect(filas).toHaveLength(6);
    expect(within(filas[2]).getByText(/da el estadístico/)).toBeInTheDocument();
    expect(within(filas[2]).getByText("fuera")).toBeInTheDocument();
    expect(within(filas[0]).getByText("dentro")).toBeInTheDocument();
  });

  it("arranca con el lag del estadístico elegido y muestra su fórmula sustituida", async () => {
    const { container } = render(<Etapa1Desglose test={makeAndersonConDesglose()} />);

    expect(screen.getByRole("button", { name: "3" })).toHaveAttribute("aria-pressed", "true");
    await waitFor(() => {
      expect(container.querySelectorAll(".katex").length).toBeGreaterThan(0);
    });
    const latex = Array.from(
      container.querySelectorAll('.katex annotation[encoding="application/x-tex"]'),
    )
      .map((n) => n.textContent)
      .join(" ");
    expect(latex).toContain("r_{3}");
    expect(latex).toContain("-620");
    expect(latex).toContain("fuera de las bandas");
  });

  it.each([
    ["el botón del número de lag", async () => fireEvent.click(screen.getByRole("button", { name: "5" })), 5],
    [
      "Enter sobre la barra enfocada con el teclado",
      async () => {
        const grafico = screen.getByRole("img", { name: /Correlograma/ });
        fireEvent.keyDown(grafico, { key: "ArrowRight" }); // primer marcador: lag 1
        fireEvent.keyDown(grafico, { key: "Enter" });
      },
      1,
    ],
  ])("elegir otro lag con %s cambia el renglón activo", async (_via, accion, lag) => {
    render(<Etapa1Desglose test={makeAndersonConDesglose()} />);

    await accion();

    expect(screen.getByRole("button", { name: String(lag) })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "3" })).toHaveAttribute("aria-pressed", "false");
  });
});

describe("Etapa1Desglose — Chow", () => {
  it("muestra un renglón por observación y resalta la de mayor z", () => {
    render(<Etapa1Desglose test={makeChowConDesglose()} />);

    const filas = within(screen.getByRole("table")).getAllByRole("row").slice(1);
    expect(filas).toHaveLength(4);
    expect(within(filas[2]).getByText(/máximo/)).toBeInTheDocument();
    expect(filas[2]).toHaveAttribute("data-activa");
    expect(filas[0]).not.toHaveAttribute("data-activa");
  });
});
