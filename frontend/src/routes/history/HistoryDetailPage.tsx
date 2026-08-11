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
        <Etapa1ResultView
          result={detail.etapa1}
          modo={(detail.modo as Modo | null) ?? "experto"}
        />
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
          <Etapa2RankingView etapa2={detail.etapa2} />
        </div>
      )}
    </div>
  );
}
