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
    render(<Etapa2RankingView etapa2={{ ranking: RANKING_13, warnings: [], puntos_empiricos: [] }} />);

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
        etapa2={{ ranking: RANKING_13.slice(0, 4), warnings: [], puntos_empiricos: [] }}
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
      <Etapa2RankingView etapa2={{ ranking: RANKING_13, warnings, puntos_empiricos: [] }} />,
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
      <Etapa2RankingView etapa2={{ ranking: RANKING_13, warnings, puntos_empiricos: [] }} />,
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
      <Etapa2RankingView etapa2={{ ranking: RANKING_13, warnings, puntos_empiricos: [] }} />,
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
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [] }}
        onElegir={onElegir}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Elegir este ajuste" }));
    expect(onElegir).toHaveBeenCalledWith("gumbel", "momentos");
  });

  it("F5 — no muestra 'Elegir este ajuste' en modo de solo lectura (sin onElegir)", () => {
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [distribucion("gumbel", 12.5)], warnings: [], puntos_empiricos: [] }}
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
        etapa2={{ ranking: [item], warnings: [], puntos_empiricos: [] }}
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
        etapa2={{ ranking: [distribucion("gumbel", 7.65775)], warnings: [], puntos_empiricos: [] }}
        mediaSerie={110}
      />,
    );
    expect(screen.getByText(/7,0 %/)).toBeInTheDocument();
  });
});
