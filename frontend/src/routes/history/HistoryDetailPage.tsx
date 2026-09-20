import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getHistoryItem } from "../../api/history";
import { postRecalcularDesignEvents } from "../../api/analysis";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import { Etapa1ResultView } from "../results/Etapa1ResultView";
import { Etapa2Explorador } from "../results/Etapa2Explorador";
import { Etapa2EventosView } from "../results/Etapa2EventosView";
import type { AnalysisDetail, Modo } from "../../api/types";
import "./HistoryDetailPage.css";

export function HistoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  // La elección registrada se muestra dentro del explorador, debajo del ranking
  // y junto a la exploración (en escritorio, lado a lado) para poder compararlas.
  const seleccion = detail.etapa2?.seleccion ?? null;
  const eleccionRegistrada = seleccion && detail.etapa2 && (
    <>
      <h3 className="h" style={{ fontSize: 14, marginBottom: 4 }}>
        Elección registrada
      </h3>
      <p className="sub" style={{ marginBottom: 8 }}>
        {seleccion.distribucion} · {seleccion.metodo} · períodos de retorno:{" "}
        {seleccion.periodos_retorno.join(", ")} ·{" "}
        {new Date(detail.created_at).toLocaleString("es-AR")}
      </p>
      <Etapa2EventosView
        eventos={{
          distribucion: seleccion.distribucion,
          metodo: seleccion.metodo,
          eventos_diseno: seleccion.eventos_diseno,
          curva_ajuste: seleccion.curva_ajuste,
        }}
        puntosEmpiricos={detail.etapa2.puntos_empiricos}
      />
    </>
  );

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

          {!seleccion && (
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
          <Etapa2Explorador
            etapa2={detail.etapa2}
            explorar={(distribucion, metodo, periodosRetorno) =>
              postRecalcularDesignEvents(detail.id, {
                distribucion,
                metodo,
                periodos_retorno: periodosRetorno,
              })
            }
            mediaSerie={detail.etapa1?.descriptive?.media}
            seleccionRegistrada={seleccion}
            eleccion={eleccionRegistrada}
          />
        </div>
      )}
    </div>
  );
}
