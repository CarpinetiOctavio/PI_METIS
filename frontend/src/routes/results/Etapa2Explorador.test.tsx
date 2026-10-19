import { StrictMode, type ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ApiError } from "../../api/client";
import type { SeleccionEtapa2 } from "../../api/types";
import { errorText } from "../../i18n/errors.es";
import { formatNum } from "../../i18n/format";
import { makeEtapa2 } from "../../test/etapa2Fixtures";
import { renderPage } from "../../test/renderPage";
import {
  Etapa2Explorador,
  type ExplorarEtapa2Fn,
  type ExplorarSimuladoFn,
  type SimulacionExplorable,
} from "./Etapa2Explorador";

const RECALCULO = {
  eventos_diseno: [{ periodo_retorno: 2, valor: 108.4 }],
  curva_ajuste: [{ periodo_retorno: 1.05, valor: 55.0 }],
};

const BOTON = { name: "Explorar este ajuste" };

function montar(explorar: ReturnType<typeof vi.fn>, eleccion?: ReactNode) {
  const { container } = renderPage(
    <Etapa2Explorador etapa2={makeEtapa2()} explorar={explorar} eleccion={eleccion} />,
  );
  return { user: userEvent.setup(), container };
}

// Cuántas cards de evento de diseño hay en el contenedor de comparación.
const COMPARACION = ".etapa2-comparacion";
const DOBLE = ".etapa2-comparacion--doble";

describe("Etapa2Explorador", () => {
  it("no explora nada hasta que el usuario lo pide, y aclara que no cambia la elección registrada", () => {
    const explorar = vi.fn();
    montar(explorar);

    expect(screen.getByText(/no cambia la elección registrada/)).toBeInTheDocument();
    expect(screen.queryByText(/No es la elección registrada/)).not.toBeInTheDocument();
    expect(explorar).not.toHaveBeenCalled();
  });

  it("al explorar llama a `explorar` con la distribución y el método elegidos y muestra el resultado como exploración", async () => {
    const explorar = vi.fn().mockResolvedValue(RECALCULO);
    const { user } = montar(explorar);

    // "gve" es la segunda card del ranking
    await user.click((await screen.findAllByRole("button", BOTON))[1]);

    expect(await screen.findByText(/No es la elección registrada/)).toBeInTheDocument();
    expect(explorar).toHaveBeenCalledTimes(1);
    expect(explorar).toHaveBeenCalledWith("gve", "ml", expect.any(Array));
  });

  it.each([
    ["un ApiError con código propio", new ApiError(400, "DIST_METHOD_NOT_FITTED", "x"), "DIST_METHOD_NOT_FITTED"],
    ["un error cualquiera (red caída, etc.)", new Error("boom"), ""],
  ])("si explorar falla con %s, muestra el texto legible del catálogo", async (_caso, falla, codigo) => {
    const { user } = montar(vi.fn().mockRejectedValue(falla));

    await user.click((await screen.findAllByRole("button", BOTON))[0]);

    expect(await screen.findByRole("alert")).toHaveTextContent(errorText(codigo));
    expect(screen.queryByText(/No es la elección registrada/)).not.toBeInTheDocument();
  });

  it("una exploración exitosa limpia el error de la anterior", async () => {
    const explorar = vi
      .fn()
      .mockRejectedValueOnce(new ApiError(400, "DIST_METHOD_NOT_FITTED", "x"))
      .mockResolvedValueOnce(RECALCULO);
    const { user } = montar(explorar);

    await user.click((await screen.findAllByRole("button", BOTON))[0]);
    expect(await screen.findByRole("alert")).toBeInTheDocument();

    await user.click((await screen.findAllByRole("button", BOTON))[0]);
    expect(await screen.findByText(/No es la elección registrada/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  // El lado a lado (escritorio, ≥ 1100px) o apilado (móvil) lo decide el CSS con
  // una media query que jsdom no evalúa: acá se fija la estructura que ese CSS
  // necesita — la elección registrada y la exploración como hermanas dentro de
  // UN mismo contenedor, marcado como doble solo cuando hay las dos.
  it("con elección registrada: se ve sola hasta que se explora; al explorar queda junto a la exploración", async () => {
    const { user, container } = montar(vi.fn().mockResolvedValue(RECALCULO), <p>ELECCION-REGISTRADA</p>);

    expect(container.querySelector(COMPARACION)).toHaveTextContent("ELECCION-REGISTRADA");
    expect(container.querySelector(DOBLE)).toBeNull();

    await user.click((await screen.findAllByRole("button", BOTON))[0]);
    await screen.findByText(/No es la elección registrada/);

    const doble = container.querySelector(DOBLE);
    expect(doble).not.toBeNull();
    expect(doble).toHaveTextContent("ELECCION-REGISTRADA");
    expect(doble).toHaveTextContent("Exploración");
  });

  it("sin elección registrada, la exploración se ve sola (nada que comparar, sin layout doble)", async () => {
    const { user, container } = montar(vi.fn().mockResolvedValue(RECALCULO));

    expect(container.querySelector(COMPARACION)).toBeNull();

    await user.click((await screen.findAllByRole("button", BOTON))[0]);
    await screen.findByText(/No es la elección registrada/);

    expect(container.querySelector(COMPARACION)).not.toBeNull();
    expect(container.querySelector(DOBLE)).toBeNull();
  });
});

// Revisión de DECISIÓN 071 (18/10/2026): explorar bajo una simulación de exclusión.
describe("Etapa2Explorador — con una simulación de exclusión vigente", () => {
  const SELECCION_SIMULADA: SeleccionEtapa2 = {
    distribucion: "gve",
    metodo: "ml",
    periodos_retorno: [2],
    eventos_diseno: [{ periodo_retorno: 2, valor: 77.7 }],
    curva_ajuste: [{ periodo_retorno: 1.05, valor: 40.0 }],
    estado: "ok",
  };
  // Tres puntos sin los excluidos, contra uno solo en makeEtapa2().
  const PUNTOS_SIMULADOS = [
    { valor: 90, periodo_retorno: 4, probabilidad: 0.75 },
    { valor: 80, periodo_retorno: 2, probabilidad: 0.5 },
    { valor: 70, periodo_retorno: 1.33, probabilidad: 0.25 },
  ];

  function simulacion(
    explorar: ExplorarSimuladoFn,
    clave = "5",
  ): SimulacionExplorable {
    return { clave, aniosExcluidos: "2005", puntosEmpiricos: PUNTOS_SIMULADOS, explorar };
  }

  function Montaje({
    explorar,
    explorarSimulado,
    vista,
    clave,
    conSimulacion = true,
  }: Readonly<{
    explorar: ExplorarEtapa2Fn;
    explorarSimulado: ExplorarSimuladoFn;
    vista: "original" | "simulada";
    clave?: string;
    conSimulacion?: boolean;
  }>) {
    return (
      <Etapa2Explorador
        etapa2={makeEtapa2()}
        explorar={explorar}
        simulacion={conSimulacion ? simulacion(explorarSimulado, clave) : null}
        vista={vista}
        selectorVista={<p>SELECTOR</p>}
      />
    );
  }

  const marcadores = (container: HTMLElement) =>
    container.querySelectorAll('.etapa2-exploracion g[data-series="empiricos"] circle').length;

  it("explorar pide la versión original y la simulada, y la vista simulada usa los puntos sin los excluidos", async () => {
    const explorar = vi.fn().mockResolvedValue(RECALCULO);
    const explorarSimulado = vi.fn().mockResolvedValue(SELECCION_SIMULADA);
    const { container } = renderPage(
      <Montaje explorar={explorar} explorarSimulado={explorarSimulado} vista="simulada" />,
    );
    const user = userEvent.setup();

    await user.click((await screen.findAllByRole("button", BOTON))[1]);

    expect(await screen.findByText(/Exploración sin los años 2005/)).toBeInTheDocument();
    expect(explorar).toHaveBeenCalledWith("gve", "ml", expect.any(Array));
    // Una sola vez aunque StrictMode repita el efecto.
    expect(explorarSimulado).toHaveBeenCalledTimes(1);
    expect(explorarSimulado).toHaveBeenCalledWith("gve", "ml", expect.any(Array));
    expect(screen.getByText(formatNum(77.7))).toBeInTheDocument();
    expect(screen.queryByText(formatNum(108.4))).not.toBeInTheDocument();
    expect(marcadores(container)).toBe(3);
    expect(screen.getByText("SELECTOR")).toBeInTheDocument();
  });

  it("la vista original muestra la exploración contra el análisis original", async () => {
    const explorarSimulado = vi.fn().mockResolvedValue(SELECCION_SIMULADA);
    const { container, rerender } = renderPage(
      <Montaje
        explorar={vi.fn().mockResolvedValue(RECALCULO)}
        explorarSimulado={explorarSimulado}
        vista="original"
      />,
    );
    const user = userEvent.setup();
    await user.click((await screen.findAllByRole("button", BOTON))[1]);

    expect(await screen.findByText(formatNum(108.4))).toBeInTheDocument();
    expect(marcadores(container)).toBe(1);

    rerender(
      <StrictMode>
        <Montaje
          explorar={vi.fn().mockResolvedValue(RECALCULO)}
          explorarSimulado={explorarSimulado}
          vista="simulada"
        />
      </StrictMode>,
    );
    expect(await screen.findByText(formatNum(77.7))).toBeInTheDocument();
  });

  it("si cambia la simulación, descarta la exploración simulada vieja y la vuelve a pedir", async () => {
    const explorar = vi.fn().mockResolvedValue(RECALCULO);
    const explorarSimulado = vi
      .fn()
      .mockResolvedValueOnce(SELECCION_SIMULADA)
      .mockResolvedValueOnce({
        ...SELECCION_SIMULADA,
        eventos_diseno: [{ periodo_retorno: 2, valor: 66.6 }],
      });
    const { rerender } = renderPage(
      <Montaje explorar={explorar} explorarSimulado={explorarSimulado} vista="simulada" />,
    );
    const user = userEvent.setup();
    await user.click((await screen.findAllByRole("button", BOTON))[1]);
    expect(await screen.findByText(formatNum(77.7))).toBeInTheDocument();

    rerender(
      <StrictMode>
        <Montaje
          explorar={explorar}
          explorarSimulado={explorarSimulado}
          vista="simulada"
          clave="5,7"
        />
      </StrictMode>,
    );

    expect(await screen.findByText(formatNum(66.6))).toBeInTheDocument();
    expect(screen.queryByText(formatNum(77.7))).not.toBeInTheDocument();
    expect(explorarSimulado).toHaveBeenCalledTimes(2);
  });

  it("si la combinación no ajusta sin los puntos, lo explica en vez de mostrar eventos vacíos", async () => {
    const explorarSimulado = vi.fn().mockResolvedValue({
      ...SELECCION_SIMULADA,
      eventos_diseno: [{ periodo_retorno: 2, valor: null }],
      curva_ajuste: [],
      estado: "no_aplicable",
    });
    renderPage(
      <Montaje
        explorar={vi.fn().mockResolvedValue(RECALCULO)}
        explorarSimulado={explorarSimulado}
        vista="simulada"
      />,
    );
    const user = userEvent.setup();
    await user.click((await screen.findAllByRole("button", BOTON))[1]);

    expect(
      await screen.findByText(/Sin los años 2005, gve · ml no se puede ajustar \(no aplicable\)/),
    ).toBeInTheDocument();
  });

  it("si sin los puntos no queda Etapa 2, lo dice", async () => {
    renderPage(
      <Montaje
        explorar={vi.fn().mockResolvedValue(RECALCULO)}
        explorarSimulado={vi.fn().mockResolvedValue(null)}
        vista="simulada"
      />,
    );
    const user = userEvent.setup();
    await user.click((await screen.findAllByRole("button", BOTON))[1]);

    expect(await screen.findByText(/no hay exploración en esta vista/)).toBeInTheDocument();
  });

  it("sin simulación vigente no pide la versión simulada", async () => {
    const explorarSimulado = vi.fn();
    renderPage(
      <Montaje
        explorar={vi.fn().mockResolvedValue(RECALCULO)}
        explorarSimulado={explorarSimulado}
        vista="original"
        conSimulacion={false}
      />,
    );
    const user = userEvent.setup();
    await user.click((await screen.findAllByRole("button", BOTON))[1]);

    expect(await screen.findByText(formatNum(108.4))).toBeInTheDocument();
    expect(explorarSimulado).not.toHaveBeenCalled();
  });
});
