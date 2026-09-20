import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderPage } from "../../test/renderPage";
import { mockChartRect } from "../../test/chartRect";
import { makeEtapa1Datos } from "../../test/etapa1Fixtures";
import type { Etapa1Datos } from "../../api/types";
import { descargarCsv } from "./exclusiones";
import { Etapa1GraficosView } from "./Etapa1GraficosView";

// La descarga real necesita URL.createObjectURL (jsdom no lo implementa): se
// reemplaza por un espía y se verifica qué archivo se habría descargado.
vi.mock("./exclusiones", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./exclusiones")>()),
  descargarCsv: vi.fn(),
}));

// Márgenes del viewBox de InteractiveChart (left 88, top 12): el clic se calcula
// desde el cx/cy del marcador más ese margen, con el rect mockeado 1:1.
const MARGEN = { left: 88, top: 12 };

function montar(overrides: Partial<Etapa1Datos> = {}, nombreArchivo?: string) {
  const { container } = renderPage(
    <Etapa1GraficosView datos={makeEtapa1Datos(overrides)} nombreArchivo={nombreArchivo} />,
  );
  const casillas = () => screen.getAllByRole("checkbox");
  const huecos = () => container.querySelectorAll("circle[data-marked]").length;
  return { container, casillas, huecos, user: userEvent.setup() };
}

describe("Etapa1GraficosView — exclusión de puntos", () => {
  beforeEach(() => {
    mockChartRect();
    vi.mocked(descargarCsv).mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("lista todos los años; Chow queda sugerido pero sin seleccionar; sin nada excluido no se puede descargar", () => {
    const { casillas, huecos } = montar();

    expect(casillas()).toHaveLength(12);
    expect(casillas().every((c) => !(c as HTMLInputElement).checked)).toBe(true);
    // el atípico de Chow (índice 5, año 2005) está señalado pero no seleccionado
    expect(screen.getAllByText("sugerido por Chow")).toHaveLength(1);
    expect(screen.getByText("sugerido por Chow").closest("label")).toHaveTextContent("2005");
    expect(screen.getByText("Ningún punto excluido.")).toBeInTheDocument();
    expect(huecos()).toBe(0);
    expect(screen.getByRole("button", { name: /Descargar serie sin los puntos/ })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Limpiar selección" })).toBeDisabled();
  });

  it("marcar un año en la lista lo dibuja hueco en los DOS gráficos; Limpiar lo deshace", async () => {
    const { casillas, huecos, user } = montar();

    await user.click(casillas()[3]);

    // el conteo vive en una región `status` (<output>): el lector de pantalla lo anuncia
    expect(screen.getByRole("status")).toHaveTextContent("1 de 12 puntos excluidos.");
    expect(huecos()).toBe(2); // serie temporal + gráfico de Chow
    expect(screen.getByRole("button", { name: /Descargar serie sin los puntos/ })).toBeEnabled();

    await user.click(screen.getByRole("button", { name: "Limpiar selección" }));

    expect(screen.getByText("Ningún punto excluido.")).toBeInTheDocument();
    expect(huecos()).toBe(0);
  });

  it("un clic sobre un punto del gráfico marca el mismo año en la lista, y otro clic lo desmarca", () => {
    const { container, casillas } = montar();
    const capture = container.querySelector(".interactive-chart__capture") as Element;
    const circulo = container.querySelectorAll('[data-series="puntos"] circle')[3];
    const posicion = {
      clientX: MARGEN.left + Number(circulo.getAttribute("cx")),
      clientY: MARGEN.top + Number(circulo.getAttribute("cy")),
    };
    const clic = () => {
      fireEvent.mouseDown(capture, posicion);
      fireEvent.mouseUp(capture, posicion);
    };

    clic();
    expect((casillas()[3] as HTMLInputElement).checked).toBe(true);
    expect(screen.getByText("1 de 12 puntos excluidos.")).toBeInTheDocument();

    clic();
    expect((casillas()[3] as HTMLInputElement).checked).toBe(false);
  });

  it("descargar entrega el CSV sin los excluidos, nombrado con el archivo original", async () => {
    const { casillas, user } = montar({}, "estacion_04.csv");

    await user.click(casillas()[0]);
    await user.click(casillas()[5]);
    await user.click(screen.getByRole("button", { name: /Descargar serie sin los puntos/ }));

    expect(descargarCsv).toHaveBeenCalledTimes(1);
    const [nombre, contenido] = vi.mocked(descargarCsv).mock.calls[0];
    expect(nombre).toBe("estacion_04_sin_atipicos.csv");
    const filas = contenido.trim().split("\n");
    expect(filas[0]).toBe("periodo,valor");
    expect(filas).toHaveLength(1 + 10); // 12 años - 2 excluidos
    expect(filas).not.toContain("2000,100");
    expect(filas).not.toContain("2005,115");
    expect(filas).toContain("2001,103");
  });

  // Avisos que acompañan a la selección: cada fila dice qué se elige, sobre qué
  // serie, y qué texto tiene que aparecer o no.
  it.each([
    ["un punto del medio: los vecinos quedarían como consecutivos", {}, [4], [/Quitar un punto del medio/], []],
    ["solo el primero: no hay hueco en medio", {}, [0], [], [/Quitar un punto del medio/]],
    ["carga mensual: lo descargado son máximos anuales", { resolucion_original: "mensual" as const }, [0], [/Tu archivo original era mensual/], []],
    ["carga diaria: lo descargado son máximos anuales", { resolucion_original: "diaria" as const }, [0], [/Tu archivo original era diaria/], []],
    ["carga anual: sin aviso de agregación", {}, [0], [], [/Tu archivo original era/]],
    ["quedarían menos de 10 datos", {}, [0, 1, 2], [/Quedarían 9 datos/], []],
    ["quedan 10 datos: sin aviso", {}, [0, 1], [], [/Quedarían/]],
  ])("%s", async (_caso, overrides, indices, presentes, ausentes) => {
    const { casillas, user } = montar(overrides);

    for (const i of indices) await user.click(casillas()[i]);

    for (const texto of presentes) expect(screen.getByText(texto)).toBeInTheDocument();
    for (const texto of ausentes) expect(screen.queryByText(texto)).not.toBeInTheDocument();
  });

  it("en la vista calendario no se puede seleccionar sobre el gráfico (otra agregación, otros índices)", async () => {
    const { user } = montar({
      resolucion_original: "mensual",
      serie_calendario: {
        serie: [1, 2, 3],
        timestamps: [
          { iso: "2000-01-01", anio: 2000 },
          { iso: "2001-01-01", anio: 2001 },
          { iso: "2002-01-01", anio: 2002 },
        ],
      },
    });

    await user.click(screen.getByRole("button", { name: "Calendario" }));

    expect(screen.getByText(/solo está disponible en la vista configurada/)).toBeInTheDocument();
  });
});
