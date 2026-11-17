import { useEffect, useRef, useState, type ReactNode } from "react";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import type { Etapa2EventosState } from "../../api/sse";
import type {
  DesignEventsRecalcResponse,
  Etapa2Result,
  PuntoEmpirico,
  SeleccionEtapa2,
} from "../../api/types";
import type { ContextoSerie } from "../../i18n/periodoRetorno";
import { textoSinAjusteSimulado } from "../../i18n/estadoMetodo";
import { Etapa2EventosView } from "./Etapa2EventosView";
import { Etapa2RankingView } from "./Etapa2RankingView";
import "./Etapa2Explorador.css";

/**
 * Recalcula los eventos de diseño de una distribución+método distintos de la
 * elección registrada. Es lo único que cambia entre los lugares donde se
 * explora: el historial y la sesión de CU-01 llaman a
 * `POST /analysis/{id}/design-events` (fuente de verdad en la BD), y CU-02 —
 * que no persiste nada — llamará a un endpoint sin id cuando exista (plan de
 * feedback de directores, ítem B, Tanda 2). El componente no sabe cuál es.
 */
export type ExplorarEtapa2Fn = (
  distribucion: string,
  metodo: string,
  periodosRetorno: number[],
) => Promise<DesignEventsRecalcResponse>;

/**
 * La misma exploración, reajustada sin los puntos excluidos de la simulación
 * vigente (revisión de DECISIÓN 071, 18/10/2026). Quien monta el componente la
 * resuelve con `POST /analysis/simulate-exclusion` y la combinación explorada en
 * `seleccion`: no hay endpoint nuevo, y sigue sin tocar la elección (DECISIÓN
 * 062). `null` si sin esos puntos no queda Etapa 2.
 */
export type ExplorarSimuladoFn = (
  distribucion: string,
  metodo: string,
  periodosRetorno: number[],
) => Promise<SeleccionEtapa2 | null>;

/** Simulación de exclusión vigente con Etapa 2, vista desde la exploración. */
export interface SimulacionExplorable {
  // Identifica la simulación (los puntos excluidos): si cambia, la exploración
  // simulada que había deja de valer y se vuelve a pedir.
  clave: string;
  aniosExcluidos: string;
  // Posiciones de Weibull sin los puntos excluidos, no las del análisis original.
  puntosEmpiricos: PuntoEmpirico[];
  explorar: ExplorarSimuladoFn;
}

// Bloque C3 (plan post-avance) — resultado de "explorar" una combinación
// distinta. Guarda distribucion/metodo elegidos junto al resultado porque el
// recálculo no los devuelve (el cliente ya los conoce, se los mandó él mismo).
interface ExploracionState {
  distribucion: string;
  metodo: string;
  eventos: Etapa2EventosState;
}

// Lo que el usuario pidió explorar. Se fija al pedir, antes de que llegue la
// respuesta original, para que la versión simulada se pida en paralelo.
interface ObjetivoExploracion {
  distribucion: string;
  metodo: string;
  periodosRetorno: number[];
}

interface ExploracionSimuladaState {
  clave: string;
  seleccion: SeleccionEtapa2 | null;
  error: string | null;
}

function claveSimulada(simulacion: SimulacionExplorable, objetivo: ObjetivoExploracion): string {
  return [
    simulacion.clave,
    objetivo.distribucion,
    objetivo.metodo,
    objetivo.periodosRetorno.join(","),
  ].join("|");
}

/**
 * Ranking de distribuciones explorable, compartido entre `HistoryDetailPage`
 * y `ResultsPage` (ítem B del plan de feedback de directores, 20/09/2026).
 *
 * DECISIÓN 062 — "explorar no es decidir": este componente nunca toca la
 * elección registrada ni vuelve a pedir el análisis. El resultado de explorar
 * vive en su propio estado, aparte de la elección, y desaparece si el usuario
 * navega fuera de la página — no hay nada que persista.
 *
 * El título de la sección lo pone quien lo monta (cada página ya tiene el
 * suyo); acá va el texto que aclara qué hace explorar.
 *
 * `eleccion` es el bloque de la elección registrada (el "Evento de diseño" que
 * el usuario eligió, o la "Elección registrada" del historial). Se renderiza
 * acá, debajo del ranking y junto a la exploración, para poder compararlas:
 * en escritorio (≥ 1100px) quedan lado a lado, en móvil apiladas (ver el CSS).
 * Mientras no se explora nada, la elección se ve sola, como siempre.
 *
 * Con una simulación de exclusión vigente (`simulacion`), cada exploración se
 * pide dos veces en paralelo: contra el análisis original y sin los puntos
 * excluidos. `vista` elige cuál se muestra, con un único selector
 * (`selectorVista`) sobre la comparación que cambia a la vez la elección y la
 * exploración: comparar una contra la otra en vistas distintas no tiene sentido.
 */
export function Etapa2Explorador({
  etapa2,
  explorar,
  mediaSerie,
  seleccionRegistrada,
  eleccion,
  contextoSerie,
  simulacion,
  vista = "original",
  selectorVista,
}: Readonly<{
  etapa2: Etapa2Result;
  explorar: ExplorarEtapa2Fn;
  mediaSerie?: number | null;
  seleccionRegistrada?: { distribucion: string; metodo: string } | null;
  eleccion?: ReactNode;
  // DECISIÓN 076: rótulos del período de retorno según la serie ajustada.
  contextoSerie?: ContextoSerie;
  simulacion?: SimulacionExplorable | null;
  vista?: "original" | "simulada";
  selectorVista?: ReactNode;
}>) {
  const [exploracion, setExploracion] = useState<ExploracionState | null>(null);
  const [explorando, setExplorando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [objetivo, setObjetivo] = useState<ObjetivoExploracion | null>(null);
  const [simulada, setSimulada] = useState<ExploracionSimuladaState | null>(null);
  // Última versión simulada pedida. Descarta respuestas viejas (cambió la
  // simulación o la combinación mientras volaba el pedido) y evita pedirla dos
  // veces bajo StrictMode, que repite el efecto conservando los refs.
  const pedidaRef = useRef<string | null>(null);

  useEffect(() => {
    if (!simulacion || !objetivo) {
      // Sin simulación vigente no hay nada que pedir; si vuelve la misma
      // simulación, se pide de nuevo.
      pedidaRef.current = null;
      return;
    }
    const clave = claveSimulada(simulacion, objetivo);
    if (pedidaRef.current === clave) return;
    pedidaRef.current = clave;
    simulacion
      .explorar(objetivo.distribucion, objetivo.metodo, objetivo.periodosRetorno)
      .then((seleccion) => {
        if (pedidaRef.current === clave) setSimulada({ clave, seleccion, error: null });
      })
      .catch((err: unknown) => {
        if (pedidaRef.current !== clave) return;
        setSimulada({
          clave,
          seleccion: null,
          error: err instanceof ApiError ? errorText(err.codigo) : errorText(""),
        });
      });
  }, [simulacion, objetivo]);

  async function handleExplorar(
    distribucion: string,
    metodo: string,
    periodosRetorno: number[],
  ) {
    setExplorando(true);
    setError(null);
    setObjetivo({ distribucion, metodo, periodosRetorno });
    try {
      const resultado = await explorar(distribucion, metodo, periodosRetorno);
      setExploracion({
        distribucion,
        metodo,
        eventos: {
          distribucion,
          metodo,
          eventos_diseno: resultado.eventos_diseno,
          curva_ajuste: resultado.curva_ajuste,
        },
      });
    } catch (err) {
      setExploracion(null);
      setError(err instanceof ApiError ? errorText(err.codigo) : errorText(""));
    } finally {
      setExplorando(false);
    }
  }

  const verSimulada = vista === "simulada" && Boolean(simulacion);
  // Solo vale la versión simulada de la simulación y la combinación actuales:
  // ninguna vista puede quedar mostrando una simulación vieja.
  const simuladaVigente =
    simulacion && objetivo && simulada?.clave === claveSimulada(simulacion, objetivo)
      ? simulada
      : null;
  const hayComparacion = Boolean(eleccion || exploracion);

  return (
    <>
      <p className="sub" style={{ marginBottom: 8 }}>
        Elegí otra combinación para explorarla — no cambia la elección
        registrada del análisis.
      </p>
      <Etapa2RankingView
        etapa2={etapa2}
        modo="exploracion"
        onElegir={handleExplorar}
        resolving={explorando}
        mediaSerie={mediaSerie}
        seleccionRegistrada={seleccionRegistrada}
        contextoSerie={contextoSerie}
      />

      {error && (
        <div className="banner crit" role="alert" style={{ marginTop: 12 }}>
          <span className="ic">!</span> {error}
        </div>
      )}

      {hayComparacion && selectorVista}

      {hayComparacion && (
        <div
          className={`etapa2-comparacion${eleccion && exploracion ? " etapa2-comparacion--doble" : ""}`}
        >
          {eleccion && <div className="etapa2-comparacion__eleccion">{eleccion}</div>}
          {exploracion && (
            <div className="etapa2-exploracion">
              {verSimulada && simulacion ? (
                <ExploracionSimulada
                  exploracion={exploracion}
                  simulada={simuladaVigente}
                  simulacion={simulacion}
                  contextoSerie={contextoSerie}
                />
              ) : (
                <>
                  <p className="sub">
                    <strong>Exploración</strong> — {exploracion.distribucion} ·{" "}
                    {exploracion.metodo}. No es la elección registrada del análisis.
                  </p>
                  <Etapa2EventosView
                    key="original"
                    eventos={exploracion.eventos}
                    puntosEmpiricos={etapa2.puntos_empiricos}
                    contextoSerie={contextoSerie}
                  />
                </>
              )}
            </div>
          )}
        </div>
      )}
    </>
  );
}

function ExploracionSimulada({
  exploracion,
  simulada,
  simulacion,
  contextoSerie,
}: Readonly<{
  exploracion: ExploracionState;
  simulada: ExploracionSimuladaState | null;
  simulacion: SimulacionExplorable;
  contextoSerie?: ContextoSerie;
}>) {
  const { distribucion, metodo } = exploracion;
  const anios = simulacion.aniosExcluidos;
  if (!simulada) {
    return (
      <p className="sub" aria-live="polite">
        Recalculando la exploración sin los años {anios}…
      </p>
    );
  }
  if (simulada.error) {
    return (
      <div className="banner crit" role="alert">
        <span className="ic">!</span> {simulada.error}
      </div>
    );
  }
  const seleccion = simulada.seleccion;
  if (!seleccion) {
    return (
      <p className="sub">
        Sin los puntos excluidos no hay Etapa 2 que recalcular (Etapa 1 queda
        rechazada), así que no hay exploración en esta vista.
      </p>
    );
  }
  if (seleccion.estado && seleccion.estado !== "ok") {
    return <p className="sub">{textoSinAjusteSimulado(distribucion, metodo, seleccion.estado, anios)}</p>;
  }
  return (
    <>
      <p className="sub">
        <strong>Exploración sin los años {anios}</strong>: {distribucion} · {metodo}. No
        es la elección registrada del análisis.
      </p>
      <Etapa2EventosView
        key="simulada"
        eventos={{
          distribucion,
          metodo,
          eventos_diseno: seleccion.eventos_diseno,
          curva_ajuste: seleccion.curva_ajuste,
        }}
        puntosEmpiricos={simulacion.puntosEmpiricos}
        contextoSerie={contextoSerie}
      />
    </>
  );
}
