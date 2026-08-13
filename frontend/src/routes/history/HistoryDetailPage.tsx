import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getHistoryItem } from "../../api/history";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import { Etapa1ResultView } from "../results/Etapa1ResultView";
import { Etapa2RankingView } from "../results/Etapa2RankingView";
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
            Ranking de distribuciones
          </h2>
          <Etapa2RankingView
            etapa2={detail.etapa2}
            mediaSerie={detail.etapa1?.descriptive?.media}
          />
        </div>
      )}
    </div>
  );
}
