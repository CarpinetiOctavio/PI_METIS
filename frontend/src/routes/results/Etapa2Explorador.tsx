import { useState, type ReactNode } from "react";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import type { Etapa2EventosState } from "../../api/sse";
import type { DesignEventsRecalcResponse, Etapa2Result } from "../../api/types";
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

// Bloque C3 (plan post-avance) — resultado de "explorar" una combinación
// distinta. Guarda distribucion/metodo elegidos junto al resultado porque el
// recálculo no los devuelve (el cliente ya los conoce, se los mandó él mismo).
interface ExploracionState {
  distribucion: string;
  metodo: string;
  eventos: Etapa2EventosState;
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
 */
export function Etapa2Explorador({
  etapa2,
  explorar,
  mediaSerie,
  seleccionRegistrada,
  eleccion,
}: Readonly<{
  etapa2: Etapa2Result;
  explorar: ExplorarEtapa2Fn;
  mediaSerie?: number | null;
  seleccionRegistrada?: { distribucion: string; metodo: string } | null;
  eleccion?: ReactNode;
}>) {
  const [exploracion, setExploracion] = useState<ExploracionState | null>(null);
  const [explorando, setExplorando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleExplorar(
    distribucion: string,
    metodo: string,
    periodosRetorno: number[],
  ) {
    setExplorando(true);
    setError(null);
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
      />

      {error && (
        <div className="banner crit" role="alert" style={{ marginTop: 12 }}>
          <span className="ic">!</span> {error}
        </div>
      )}

      {(eleccion || exploracion) && (
        <div
          className={`etapa2-comparacion${eleccion && exploracion ? " etapa2-comparacion--doble" : ""}`}
        >
          {eleccion && <div className="etapa2-comparacion__eleccion">{eleccion}</div>}
          {exploracion && (
            <div className="etapa2-exploracion">
              <p className="sub">
                <strong>Exploración</strong> — {exploracion.distribucion} ·{" "}
                {exploracion.metodo}. No es la elección registrada del análisis.
              </p>
              <Etapa2EventosView
                eventos={exploracion.eventos}
                puntosEmpiricos={etapa2.puntos_empiricos}
              />
            </div>
          )}
        </div>
      )}
    </>
  );
}
