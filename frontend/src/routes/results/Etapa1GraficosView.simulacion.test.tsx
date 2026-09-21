import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderPage } from "../../test/renderPage";
import { mockChartRect } from "../../test/chartRect";
import { makeEtapa1Datos } from "../../test/etapa1Fixtures";
import { makeEtapa1Result, makeSimulacion } from "../../test/simulacionFixtures";
import { makeEtapa2 } from "../../test/etapa2Fixtures";
import { ApiError } from "../../api/client";
import type { SimulateExclusionResponse } from "../../api/types";
import { Etapa1GraficosView } from "./Etapa1GraficosView";

// El what-if de atípicos (A2) contra un `simular` mockeado: el endpoint todavía
// no existe en el backend, así que esto fija el contrato que la vista espera.
const RECALCULAR = /Recalcular sin los puntos seleccionados/;

function montar(simular?: (i: number[]) => Promise<SimulateExclusionResponse>) {
  renderPage(
    <Etapa1GraficosView
      datos={makeEtapa1Datos()}
      resultado={makeEtapa1Result()}
      simular={simular}
    />,
  );
  return {
    user: userEvent.setup(),
    casillas: () => screen.getAllByRole("checkbox"),
  };
}

describe("Etapa1GraficosView — recalcular sin los puntos (A2)", () => {
  beforeEach(() => {
    mockChartRect();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("sin `simular` no hay botón de recalcular (queda la exclusión de A1)", () => {
    montar(undefined);
    expect(screen.queryByRole("button", { name: RECALCULAR })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Descargar serie/ })).toBeInTheDocument();
  });

  it("el botón espera una selección y le pasa a `simular` los índices elegidos", async () => {
    const simular = vi.fn().mockResolvedValue(makeSimulacion());
    const { user, casillas } = montar(simular);

    expect(screen.getByRole("button", { name: RECALCULAR })).toBeDisabled();
    await user.click(casillas()[7]);
    await user.click(casillas()[5]);
    await user.click(screen.getByRole("button", { name: RECALCULAR }));

    expect(simular).toHaveBeenCalledWith([5, 7]);
  });

  it("muestra qué se quitó, el n de cada lado y los veredictos que cambiaron", async () => {
    const { user, casillas } = montar(vi.fn().mockResolvedValue(makeSimulacion()));

    await user.click(casillas()[5]);
    await user.click(screen.getByRole("button", { name: RECALCULAR }));

    const tarjeta = (await screen.findByText("Resultados sin los puntos excluidos")).closest(".card") as HTMLElement;
    expect(within(tarjeta).getByText(/Se quitó:/)).toHaveTextContent("2005");
    expect(tarjeta).toHaveTextContent("Datos: 12 → 11.");
    const anderson = within(tarjeta).getByText("anderson").closest("tr") as HTMLElement;
    expect(anderson).toHaveAttribute("data-cambio");
    expect(anderson).toHaveTextContent("aprobada");
    expect(anderson).toHaveTextContent("rechazada");
    expect(within(anderson).getByText("cambió")).toBeInTheDocument();
    expect(within(tarjeta).getByText("helmert").closest("tr")).not.toHaveAttribute("data-cambio");
    expect(tarjeta).toHaveTextContent("2 veredictos cambian al quitar esos puntos.");
    // Aviso nuevo de la corrida simulada (año del medio quitado).
    expect(within(tarjeta).getByText("El espaciado temporal es irregular.")).toBeInTheDocument();
  });

  it("si cambia la selección después de calcular, avisa que lo mostrado quedó desactualizado", async () => {
    const { user, casillas } = montar(vi.fn().mockResolvedValue(makeSimulacion()));

    await user.click(casillas()[5]);
    await user.click(screen.getByRole("button", { name: RECALCULAR }));
    await screen.findByText("Resultados sin los puntos excluidos");
    expect(screen.queryByText(/La selección cambió después de este cálculo/)).not.toBeInTheDocument();

    await user.click(casillas()[2]);
    expect(screen.getByText(/La selección cambió después de este cálculo/)).toBeInTheDocument();
  });

  it("Limpiar selección también descarta la comparación", async () => {
    const { user, casillas } = montar(vi.fn().mockResolvedValue(makeSimulacion()));

    await user.click(casillas()[5]);
    await user.click(screen.getByRole("button", { name: RECALCULAR }));
    await screen.findByText("Resultados sin los puntos excluidos");
    await user.click(screen.getByRole("button", { name: "Limpiar selección" }));

    expect(screen.queryByText("Resultados sin los puntos excluidos")).not.toBeInTheDocument();
  });

  it("con Etapa 2 en la respuesta, muestra el ranking sin esos puntos", async () => {
    const { user, casillas } = montar(
      vi.fn().mockResolvedValue(makeSimulacion({ etapa2: makeEtapa2() })),
    );

    await user.click(casillas()[5]);
    await user.click(screen.getByRole("button", { name: RECALCULAR }));

    expect(await screen.findByText("Ranking de distribuciones sin esos puntos")).toBeInTheDocument();
  });

  it("si el backend rechaza el pedido muestra el error y no una comparación", async () => {
    const { user, casillas } = montar(
      vi.fn().mockRejectedValue(new ApiError(400, "CONTRACT_SERIES_TOO_SHORT", "x")),
    );

    await user.click(casillas()[5]);
    await user.click(screen.getByRole("button", { name: RECALCULAR }));

    expect(await screen.findByRole("alert")).toHaveTextContent("menos de 10 datos");
    expect(screen.queryByText("Resultados sin los puntos excluidos")).not.toBeInTheDocument();
  });

  it("si la serie sin esos puntos queda bloqueada por contrato, lo dice en vez de armar la tabla", async () => {
    const bloqueada = makeSimulacion();
    bloqueada.etapa1.contract = { bloqueante: true, codigo_error: "CONTRACT_SERIES_TOO_SHORT", warnings: [] };
    const { user, casillas } = montar(vi.fn().mockResolvedValue(bloqueada));

    await user.click(casillas()[5]);
    await user.click(screen.getByRole("button", { name: RECALCULAR }));

    const tarjeta = (await screen.findByText("Resultados sin los puntos excluidos")).closest(".card") as HTMLElement;
    expect(within(tarjeta).getByRole("alert")).toHaveTextContent("menos de 10 datos");
    expect(within(tarjeta).queryByRole("table")).not.toBeInTheDocument();
  });

  it("no permite recalcular si quedarían menos de 10 datos", async () => {
    const { user, casillas } = montar(vi.fn());

    for (const i of [0, 1, 2]) await user.click(casillas()[i]); // 12 - 3 = 9

    expect(screen.getByRole("button", { name: RECALCULAR })).toBeDisabled();
  });
});
