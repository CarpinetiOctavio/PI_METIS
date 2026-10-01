import { describe, expect, it, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Etapa2RankingView } from "./Etapa2RankingView";
import type { DistribucionResult, MetodoStatus, WarningItem } from "../../api/types";

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

// Una distribución sin ningún método "ok": todos con el mismo status, o
// mezclados ("mixto"). Como las devuelve el backend: mejor_metodo/mejor_eea null.
function sinAjuste(nombre: string, status: MetodoStatus | "mixto"): DistribucionResult {
  const estados: MetodoStatus[] = status === "mixto" ? ["no_converge", "no_aplicable"] : [status, status];
  return {
    distribucion: nombre,
    n_parametros: 2,
    mejor_eea: null,
    mejor_metodo: null,
    metodos: estados.map((s, i) => ({ metodo: `m${i}`, parametros: {}, eea: null, status: s })),
  };
}

function etapa2Con(ranking: DistribucionResult[]) {
  return { ranking, warnings: [], puntos_empiricos: [], seleccion: null };
}

describe("Etapa2RankingView — distribuciones sin ningún ajuste posible (F3)", () => {
  // 8 con ajuste + 5 sin ajuste al final, como con una serie con negativos.
  const RANKING_NEGATIVOS = [
    ...RANKING_13.slice(0, 8),
    ...["ln2p", "lp3", "gamma2p", "expb", "genexp"].map((n) => sinAjuste(n, "disabled_negatives")),
  ];

  it.each([
    ["todos disabled_negatives", "disabled_negatives" as const, "no aplica: la serie tiene valores negativos"],
    ["todos disabled_zeros", "disabled_zeros" as const, "deshabilitada por ceros"],
    ["status mezclados", "mixto" as const, "sin ajuste posible con esta serie"],
  ])("%s: card atenuada, sin 'Mejor ajuste' y con la píldora del motivo", (_caso, status, motivo) => {
    const { container } = render(<Etapa2RankingView etapa2={etapa2Con([sinAjuste("lp3", status)])} />);

    expect(container.querySelector(".etapa2-card--sin-ajuste")).toBeInTheDocument();
    expect(screen.queryByText(/Mejor ajuste/)).not.toBeInTheDocument();
    expect(container.querySelector(".etapa2-card__motivo .pill")).toHaveTextContent(motivo);
    // sin ninguna ajustada, se ven directo bajo su subtítulo, sin botón de por medio
    expect(screen.getByText("Sin ajuste posible con esta serie (1)")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Ver (las|solo)/ })).not.toBeInTheDocument();
  });

  it("una distribución con al menos un método ok no se atenúa", () => {
    const { container } = render(<Etapa2RankingView etapa2={etapa2Con([distribucion("gumbel", 5)])} />);

    expect(container.querySelector(".etapa2-card--sin-ajuste")).not.toBeInTheDocument();
    expect(screen.getByText(/Mejor ajuste: momentos/)).toBeInTheDocument();
  });

  it("el botón cuenta por separado las restantes y las sin ajuste, que van bajo su propio subtítulo", async () => {
    const user = userEvent.setup();
    render(<Etapa2RankingView etapa2={etapa2Con(RANKING_NEGATIVOS)} />);

    expect(screen.queryByText("ln2p")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Ver las 4 restantes · 5 sin ajuste" }));

    expect(screen.getByText("Sin ajuste posible con esta serie (5)")).toBeInTheDocument();
    expect(screen.getByText("ln2p")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Ver solo las 4 mejores" })).toBeInTheDocument();
  });

  it("con 4 o menos ajustadas, el botón solo ofrece las sin ajuste", () => {
    render(<Etapa2RankingView etapa2={etapa2Con([...RANKING_13.slice(0, 3), sinAjuste("lp3", "disabled_zeros")])} />);

    expect(screen.getByRole("button", { name: "Ver las 1 sin ajuste posible" })).toBeInTheDocument();
  });

  it("no reordena: una sin ajuste en el medio queda en su lugar, solo atenuada", () => {
    const ranking = [distribucion("a", 1), sinAjuste("medio", "no_aplicable"), distribucion("b", 2)];
    const { container } = render(<Etapa2RankingView etapa2={etapa2Con(ranking)} />);

    const nombres = [...container.querySelectorAll(".etapa2-card h3")].map((h) => h.textContent);
    expect(nombres).toEqual(["a", "medio", "b"]);
    expect(screen.queryByText(/Sin ajuste posible con esta serie \(/)).not.toBeInTheDocument();
  });
});

describe("Etapa2RankingView — distribución pendiente de validación (DECISIÓN 074)", () => {
  function pareto(eea: number, conCampo = true): DistribucionResult {
    return {
      ...distribucion("gen_pareto", eea),
      metodos: [
        { metodo: "momentos", parametros: { a: 1 }, eea, status: "ok" },
        { metodo: "mc", parametros: { a: 1 }, eea: eea + 1, status: "ok" },
      ],
      ...(conCampo ? { pendiente_validacion: true } : {}),
    };
  }

  it("la card se ve, con su tabla, pero sin ningún botón para elegir ni explorar", async () => {
    const user = userEvent.setup();
    const onElegir = vi.fn();
    const { container } = render(
      <Etapa2RankingView etapa2={etapa2Con([distribucion("gumbel", 5), pareto(9)])} modo="exploracion" onElegir={onElegir} />,
    );

    // al final del ranking queda tras el botón de expandir, bajo su subtítulo
    await user.click(screen.getByRole("button", { name: "Ver 1 pendiente de validación" }));
    const card = container.querySelector(".etapa2-card--pendiente") as HTMLElement;
    expect(within(card).getByText("pendiente de validación")).toHaveClass("pill");
    expect(within(card).getByText(/No se puede elegir en esta versión/)).toBeInTheDocument();
    expect(within(card).queryByRole("button", { name: /Explorar/ })).not.toBeInTheDocument();

    await user.click(within(card).getByRole("button", { name: /Ver los 2 métodos/ }));
    expect(within(card).getByRole("table")).toBeInTheDocument();
    expect(within(card).queryByRole("button", { name: /^Explorar$|^Elegir$/ })).not.toBeInTheDocument();
  });

  it("análisis viejo sin el campo y con Pareto primera: queda en su lugar, atenuada, y 'menor EEA' va a la segunda", () => {
    const viejo = [pareto(3, false), distribucion("gumbel", 5), distribucion("normal", 6)];
    const { container } = render(<Etapa2RankingView etapa2={etapa2Con(viejo)} />);

    const cards = [...container.querySelectorAll(".etapa2-card")] as HTMLElement[];
    expect(cards.map((c) => c.querySelector("h3")?.textContent)).toEqual(["gen_pareto", "gumbel", "normal"]);
    expect(cards[0]).toHaveClass("etapa2-card--pendiente");
    expect(within(cards[0]).queryByText("menor EEA")).not.toBeInTheDocument();
    expect(within(cards[1]).getByText("menor EEA")).toBeInTheDocument();
  });

  it("al final va bajo su subtítulo, después de las sin ajuste, y el botón la cuenta aparte", async () => {
    const user = userEvent.setup();
    const ranking = [...RANKING_13.slice(0, 6), sinAjuste("lp3", "disabled_negatives"), pareto(30)];
    render(<Etapa2RankingView etapa2={etapa2Con(ranking)} />);

    await user.click(
      screen.getByRole("button", { name: "Ver las 2 restantes · 1 sin ajuste · 1 pendiente de validación" }),
    );

    const subtitulos = screen.getAllByText(/^(Sin ajuste posible con esta serie|Pendiente de validación) \(/);
    expect(subtitulos.map((s) => s.textContent)).toEqual([
      "Sin ajuste posible con esta serie (1)",
      "Pendiente de validación (1)",
    ]);
  });
});

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

  it("F1/F2 — la tabla de métodos va en un contenedor con scroll y el estado 'ok' es un punto con aria-label", async () => {
    const user = userEvent.setup();
    const dist: DistribucionResult = {
      distribucion: "gumbel",
      n_parametros: 2,
      mejor_eea: 5,
      mejor_metodo: "momentos",
      metodos: [
        { metodo: "momentos", parametros: { a: 1 }, eea: 5, status: "ok" },
        { metodo: "mv", parametros: {}, eea: null, status: "no_converge" },
      ],
    };
    const { container } = render(
      <Etapa2RankingView
        etapa2={{ ranking: [dist], warnings: [], puntos_empiricos: [], seleccion: null }}
      />,
    );

    await user.click(screen.getByRole("button", { name: /Ver los 2 métodos/ }));

    expect(container.querySelector(".etapa2-metodos-scroll")).not.toBeNull();
    // status "ok" → punto de color, sin el texto redundante "ajustado"
    expect(screen.getByRole("img", { name: "ajustado" })).toBeInTheDocument();
    expect(screen.queryByText("ajustado")).not.toBeInTheDocument();
    // status distinto de "ok" → sigue con el pill de texto completo
    expect(screen.getByText("no converge")).toBeInTheDocument();
  });

  // Ítem C: cada estado que no es "ok" se explica con su propio texto, para que
  // "no aplica por negativos" no se confunda con un fallo numérico.
  it.each([
    ["no_converge", "no converge"],
    ["no_aplicable", "no aplicable"],
    ["disabled_zeros", "deshabilitada por ceros"],
    ["disabled_negatives", "no aplica: la serie tiene valores negativos"],
  ] as const)("el estado %s se muestra como «%s»", async (status, texto) => {
    const user = userEvent.setup();
    const dist: DistribucionResult = {
      distribucion: "lognormal2p",
      n_parametros: 2,
      mejor_eea: null,
      mejor_metodo: null,
      metodos: [{ metodo: "momentos", parametros: {}, eea: null, status }],
    };
    render(
      <Etapa2RankingView
        etapa2={{ ranking: [dist], warnings: [], puntos_empiricos: [], seleccion: null }}
      />,
    );

    await user.click(screen.getByRole("button", { name: /Ver los 1 métodos/ }));

    // dentro de la tabla: el mismo rótulo puede estar también en la píldora de
    // la card (F3, motivo de una distribución sin ajuste)
    expect(within(screen.getByRole("table")).getByText(texto)).toBeInTheDocument();
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
