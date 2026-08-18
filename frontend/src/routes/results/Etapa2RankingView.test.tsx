import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Etapa2RankingView } from "./Etapa2RankingView";
import type { DistribucionResult, WarningItem } from "../../api/types";

function distribucion(nombre: string, eea: number): DistribucionResult {
  return {
    distribucion: nombre,
    n_parametros: 2,
    mejor_eea: eea,
    mejor_metodo: "momentos",
    metodos: [{ metodo: "momentos", parametros: { a: 1 }, eea, status: "ok" }],
  };
}

const RANKING_13 = Array.from({ length: 13 }, (_, i) => distribucion(`dist-${i}`, 10 + i));

describe("Etapa2RankingView", () => {
  it("F3 — muestra solo las primeras 4 distribuciones y un botón para ver el resto", async () => {
    const user = userEvent.setup();
    render(<Etapa2RankingView etapa2={{ ranking: RANKING_13, warnings: [], puntos_empiricos: [], seleccion: null }} />);

    expect(screen.getByText("dist-0")).toBeInTheDocument();
    expect(screen.getByText("dist-3")).toBeInTheDocument();
    expect(screen.queryByText("dist-4")).not.toBeInTheDocument();

    const boton = screen.getByRole("button", { name: /Ver las 9 distribuciones restantes/ });
    await user.click(boton);

    expect(screen.getByText("dist-4")).toBeInTheDocument();
    expect(screen.getByText("dist-12")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Ver solo las 4 mejores/ }),
    ).toBeInTheDocument();
  });

  it("no muestra el botón de 'ver más' cuando hay 4 o menos distribuciones", () => {
    render(
      <Etapa2RankingView
        etapa2={{ ranking: RANKING_13.slice(0, 4), warnings: [], puntos_empiricos: [], seleccion: null }}
      />,
    );
    expect(screen.queryByText(/distribuciones restantes/)).not.toBeInTheDocument();
  });

  it("F4 — 25 warnings del mismo código normal se agrupan en un solo banner con el conteo", () => {
    const warnings: WarningItem[] = Array.from({ length: 25 }, (_, i) => ({
      codigo: "DIST_HIGH_EEA",
      nivel: "normal",
      descripcion: `dist-${i}/momentos supera el 5% de la media`,
    }));
    render(
      <Etapa2RankingView etapa2={{ ranking: RANKING_13, warnings, puntos_empiricos: [], seleccion: null }} />,
    );

    expect(screen.getByText(/25 combinaciones/)).toBeInTheDocument();
    // El detalle completo sigue disponible dentro del <details>, no se pierde.
    expect(screen.getByText(/dist-24\/momentos supera el 5% de la media/)).toBeInTheDocument();
  });

  it("F4 — un warning crítico nunca se agrupa, aunque se repita más de 3 veces", () => {
    const warnings: WarningItem[] = Array.from({ length: 5 }, (_, i) => ({
      codigo: "ALGO_CRITICO",
      nivel: "critico",
      descripcion: `crítico ${i}`,
    }));
    render(
      <Etapa2RankingView etapa2={{ ranking: RANKING_13, warnings, puntos_empiricos: [], seleccion: null }} />,
    );

    for (let i = 0; i < 5; i++) {
      expect(screen.getByText(`crítico ${i}`)).toBeInTheDocument();
    }
    expect(screen.queryByText(/combinaciones/)).not.toBeInTheDocument();
  });

  it("F4 — no agrupa cuando el código se repite 3 veces o menos", () => {
    const warnings: WarningItem[] = Array.from({ length: 3 }, (_, i) => ({
      codigo: "DIST_HIGH_EEA",
      nivel: "normal",
      descripcion: `warning ${i}`,
    }));
    render(
      <Etapa2RankingView etapa2={{ ranking: RANKING_13, warnings, puntos_empiricos: [], seleccion: null }} />,
    );

    for (let i = 0; i < 3; i++) {
      expect(screen.getByText(`warning ${i}`)).toBeInTheDocument();
    }
  });

  it("F5 — el botón 'Elegir este ajuste' llama a onElegir con el mejor método", async () => {
    const user = userEvent.setup();
    const onElegir = vi.fn();
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [], seleccion: null }}
        onElegir={onElegir}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Elegir este ajuste" }));
    expect(onElegir).toHaveBeenCalledWith(
      "gumbel",
      "momentos",
      [2, 5, 10, 25, 50, 100, 200, 500],
    );
  });

  it("F5 — no muestra 'Elegir este ajuste' en modo de solo lectura (sin onElegir)", () => {
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [], seleccion: null }}
      />,
    );
    expect(
      screen.queryByRole("button", { name: "Elegir este ajuste" }),
    ).not.toBeInTheDocument();
  });

  it("F5 — no muestra 'Elegir este ajuste' cuando mejor_metodo es null", () => {
    const item = distribucion("uniforme", 1);
    item.mejor_metodo = null;
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [item], warnings: [], puntos_empiricos: [], seleccion: null }}
        onElegir={vi.fn()}
      />,
    );
    expect(
      screen.queryByRole("button", { name: "Elegir este ajuste" }),
    ).not.toBeInTheDocument();
  });

  it("F4 (magnitud) — muestra el EEA como % de la media cuando mediaSerie está disponible", () => {
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 7.65775)], warnings: [], puntos_empiricos: [], seleccion: null }}
        mediaSerie={110}
      />,
    );
    expect(screen.getByText(/7,0 %/)).toBeInTheDocument();
  });

  it("F6 — no muestra el campo de períodos de retorno en modo de solo lectura", () => {
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [], seleccion: null }}
      />,
    );
    expect(
      screen.queryByLabelText(/Períodos de retorno/),
    ).not.toBeInTheDocument();
  });

  it("F6 — manda los períodos editados en vez del default", async () => {
    const user = userEvent.setup();
    const onElegir = vi.fn();
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [], seleccion: null }}
        onElegir={onElegir}
      />,
    );

    const campo = screen.getByLabelText(/Períodos de retorno/);
    await user.clear(campo);
    await user.type(campo, "2, 10, 100");
    await user.click(screen.getByRole("button", { name: "Elegir este ajuste" }));

    expect(onElegir).toHaveBeenCalledWith("gumbel", "momentos", [2, 10, 100]);
  });

  it("F6 — rechaza un período ≤ 1 con un error inline, sin llamar a onElegir", async () => {
    const user = userEvent.setup();
    const onElegir = vi.fn();
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [], seleccion: null }}
        onElegir={onElegir}
      />,
    );

    const campo = screen.getByLabelText(/Períodos de retorno/);
    await user.clear(campo);
    await user.type(campo, "1, 10");
    await user.click(screen.getByRole("button", { name: "Elegir este ajuste" }));

    expect(onElegir).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent(/mayores que 1/);
  });

  it("F6 — rechaza más de 20 valores con un error inline, sin llamar a onElegir", async () => {
    const user = userEvent.setup();
    const onElegir = vi.fn();
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [], seleccion: null }}
        onElegir={onElegir}
      />,
    );

    const campo = screen.getByLabelText(/Períodos de retorno/);
    const veintiuno = Array.from({ length: 21 }, (_, i) => i + 2).join(", ");
    await user.clear(campo);
    await user.type(campo, veintiuno);
    await user.click(screen.getByRole("button", { name: "Elegir este ajuste" }));

    expect(onElegir).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent(/no se pueden pedir más de 20/i);
  });

  // Bloque C3 (plan post-avance) — modo "exploracion": mismo botón activo,
  // pero el callback pega al recálculo stateless, no a distribution-decision
  // — el texto tiene que leerse distinto para que nunca se confunda con
  // decidir (DECISIÓN 062).
  it("C3 — modo exploracion muestra 'Explorar este ajuste' en vez de 'Elegir este ajuste'", () => {
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [], seleccion: null }}
        modo="exploracion"
        onElegir={vi.fn()}
      />,
    );

    expect(
      screen.getByRole("button", { name: "Explorar este ajuste" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Elegir este ajuste" }),
    ).not.toBeInTheDocument();
  });

  it("C3 — modo exploracion llama a onElegir igual que stream, solo cambia el texto", async () => {
    const user = userEvent.setup();
    const onElegir = vi.fn();
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [], seleccion: null }}
        modo="exploracion"
        onElegir={onElegir}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Explorar este ajuste" }));
    expect(onElegir).toHaveBeenCalledWith(
      "gumbel",
      "momentos",
      [2, 5, 10, 25, 50, 100, 200, 500],
    );
  });

  it("C3 — seleccionRegistrada marca la card correspondiente como 'elegida en el análisis'", () => {
    render(
      <Etapa2RankingView
        etapa2={{
          ranking: [distribucion("gumbel", 12.5), distribucion("gve", 20)],
          warnings: [],
          puntos_empiricos: [],
          seleccion: null,
        }}
        modo="exploracion"
        onElegir={vi.fn()}
        seleccionRegistrada={{ distribucion: "gve", metodo: "momentos" }}
      />,
    );

    expect(screen.getByText("elegida en el análisis")).toBeInTheDocument();
    // La card "gumbel" no es la elegida — no lleva la etiqueta.
    const cardGumbel = screen.getByText("gumbel").closest(".etapa2-card");
    expect(cardGumbel).not.toHaveTextContent("elegida en el análisis");
  });

  it("C3 — sin seleccionRegistrada, ninguna card muestra 'elegida en el análisis'", () => {
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [], seleccion: null }}
        modo="lectura"
      />,
    );

    expect(screen.queryByText("elegida en el análisis")).not.toBeInTheDocument();
  });
});
