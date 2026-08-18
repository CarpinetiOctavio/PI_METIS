import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getHistoryItem } from "../../api/history";
import { postRecalcularDesignEvents } from "../../api/analysis";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import { Etapa1ResultView } from "../results/Etapa1ResultView";
import { Etapa2RankingView } from "../results/Etapa2RankingView";
import { Etapa2EventosView } from "../results/Etapa2EventosView";
import type { Etapa2EventosState } from "../../api/sse";
import type { AnalysisDetail, Modo } from "../../api/types";
import "./HistoryDetailPage.css";

// Bloque C3 (plan post-avance) — resultado de "explorar" una combinación
// distinta desde el historial. Guarda distribucion/metodo elegidos junto
// al resultado porque POST /analysis/{id}/design-events no los devuelve
// (el cliente ya los conoce, se los mandó él mismo).
interface ExploracionState {
  distribucion: string;
  metodo: string;
  eventos: Etapa2EventosState;
}

export function HistoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [exploracion, setExploracion] = useState<ExploracionState | null>(null);
  const [explorando, setExplorando] = useState(false);
  const [exploracionError, setExploracionError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    getHistoryItem(id)
      .then((data) => {
        if (!cancelled) setDetail(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof ApiError ? errorText(err.codigo) : errorText(""));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  // DECISIÓN 062 — "explorar no es decidir": este handler nunca toca
  // `detail` ni vuelve a pedir GET /history/{id}. El resultado de explorar
  // vive en su propio estado, aparte de la elección registrada, y
  // desaparece si el usuario navega fuera de la página — no hay nada que
  // persista.
  async function handleExplorar(
    distribucion: string,
    metodo: string,
    periodosRetorno: number[],
  ) {
    if (!id) return;
    setExplorando(true);
    setExploracionError(null);
    try {
      const resultado = await postRecalcularDesignEvents(id, {
        distribucion,
        metodo,
        periodos_retorno: periodosRetorno,
      });
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
      setExploracionError(err instanceof ApiError ? errorText(err.codigo) : errorText(""));
    } finally {
      setExplorando(false);
    }
  }

  if (error) {
    return (
      <div className="banner crit" role="alert">
        <span className="ic">!</span> {error}
      </div>
    );
  }

  if (!detail) {
    return <p className="sub">Cargando análisis…</p>;
  }

  return (
    <div className="history-detail-page">
      <h1 className="h">Detalle del análisis</h1>
      <p className="sub">
        {detail.tipo_variable} · {new Date(detail.created_at).toLocaleString("es-AR")}
      </p>
      {detail.etapa1 ? (
        <>
          <Etapa1ResultView
            result={detail.etapa1}
            modo={(detail.modo as Modo | null) ?? "experto"}
            mesInicioAnio={detail.configuracion?.mes_inicio_anio}
          />
          {/* PR 5 del plan de cierre de pendientes no-test (DECISIÓN 058
              §4) — sin backfill, `timestamps` es null para cualquier
              análisis persistido antes de la migración 005. Etapa1ResultView
              ya no renderiza sus gráficos en silencio (result.datos
              tampoco existe en un registro tan viejo) — acá se explica
              por qué, en vez de dejar una sección vacía sin contexto. */}
          {detail.timestamps === null && (
            <div className="banner warn" style={{ marginTop: 14 }}>
              <span className="ic">▲</span> Este análisis es anterior a esta
              versión de METIS — los gráficos de serie temporal, Chow y
              boxplot mensual no están disponibles para registros de esta
              antigüedad.
            </div>
          )}
        </>
      ) : (
        <div className="banner warn">
          <span className="ic">▲</span> Este análisis no tiene resultados de Etapa 1
          registrados.
        </div>
      )}
      {detail.etapa2 && (
        <div style={{ marginTop: 20 }}>
          <h2 className="h" style={{ fontSize: 16, marginBottom: 0 }}>
            Etapa 2 — análisis de frecuencia
          </h2>

          {detail.etapa2.seleccion ? (
            <div style={{ marginTop: 12 }}>
              <h3 className="h" style={{ fontSize: 14, marginBottom: 4 }}>
                Elección registrada
              </h3>
              <p className="sub" style={{ marginBottom: 8 }}>
                {detail.etapa2.seleccion.distribucion} ·{" "}
                {detail.etapa2.seleccion.metodo} · períodos de retorno:{" "}
                {detail.etapa2.seleccion.periodos_retorno.join(", ")} ·{" "}
                {new Date(detail.created_at).toLocaleString("es-AR")}
              </p>
              <Etapa2EventosView
                eventos={{
                  distribucion: detail.etapa2.seleccion.distribucion,
                  metodo: detail.etapa2.seleccion.metodo,
                  eventos_diseno: detail.etapa2.seleccion.eventos_diseno,
                  curva_ajuste: detail.etapa2.seleccion.curva_ajuste,
                }}
                puntosEmpiricos={detail.etapa2.puntos_empiricos}
              />
            </div>
          ) : (
            <div className="banner warn" style={{ marginTop: 12 }}>
              <span className="ic">▲</span> Este análisis tiene Etapa 2
              ejecutada pero es anterior a esta versión de METIS — no quedó
              registrada ninguna distribución elegida. Podés explorar la
              grilla igual, pero no hay una elección de referencia para
              comparar.
            </div>
          )}

          <h3 className="h" style={{ fontSize: 14, marginTop: 20, marginBottom: 4 }}>
            Ranking de distribuciones
          </h3>
          <p className="sub" style={{ marginBottom: 8 }}>
            Elegí otra combinación para explorarla — no cambia la elección
            registrada del análisis.
          </p>
          <Etapa2RankingView
            etapa2={detail.etapa2}
            modo="exploracion"
            onElegir={handleExplorar}
            resolving={explorando}
            mediaSerie={detail.etapa1?.descriptive?.media}
            seleccionRegistrada={detail.etapa2.seleccion}
          />

          {exploracionError && (
            <div className="banner crit" role="alert" style={{ marginTop: 12 }}>
              <span className="ic">!</span> {exploracionError}
            </div>
          )}

          {exploracion && (
            <div className="history-detail-exploracion" style={{ marginTop: 16 }}>
              <p className="sub">
                <strong>Exploración</strong> — {exploracion.distribucion} ·{" "}
                {exploracion.metodo}. No es la elección registrada del
                análisis.
              </p>
              <Etapa2EventosView
                eventos={exploracion.eventos}
                puntosEmpiricos={detail.etapa2.puntos_empiricos}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
