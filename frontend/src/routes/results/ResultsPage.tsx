import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import { postRecalcularDesignEvents } from "../../api/analysis";
import { Etapa1ResultView } from "./Etapa1ResultView";
import { Etapa2Explorador } from "./Etapa2Explorador";
import { Etapa2RankingView } from "./Etapa2RankingView";
import { Etapa2EventosView } from "./Etapa2EventosView";
import type { Etapa1Result, Modo } from "../../api/types";
import type { Etapa2EventosState, Etapa2RankingState } from "../../api/sse";
import "./ResultsPage.css";

interface ResultsLocationState {
  result?: Etapa1Result;
  analysisId?: string | null;
  modo?: Modo;
  etapa2?: Etapa2RankingState | null;
  eventosDiseno?: Etapa2EventosState | null;
  // Bloque F5 (DECISIÓN 057) — solo viaja en la sesión interactiva, ver la
  // nota de Etapa1ResultView sobre por qué no llega desde el historial.
  mesInicioAnio?: number;
}

export function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthed } = useAuth();

  const locationState = location.state as ResultsLocationState | null;
  const result = locationState?.result;

  useEffect(() => {
    if (!result) navigate("/config", { replace: true });
  }, [result, navigate]);

  if (!result) return null;

  // UX-D — anónimo siempre ve la presentación Experto, sin acordeón.
  const modoEfectivo: Modo = isAuthed ? (locationState?.modo ?? "experto") : "experto";

  const etapa2 = locationState?.etapa2;
  const eventosDiseno = locationState?.eventosDiseno;
  // Solo CU-01 persiste el análisis y devuelve un `analysis_id` — con él se
  // puede explorar otra distribución contra la BD (`POST /analysis/{id}/
  // design-events`, DECISIÓN 062). CU-02 (anónimo, sin id) sigue de solo
  // lectura hasta que exista el endpoint de exploración sin id (plan de
  // feedback de directores, ítem B, Tanda 2).
  const analysisId = locationState?.analysisId ?? null;
  // Lo que llega por el stream es el ranking en el momento de la pausa: todavía
  // no hay elección registrada (`seleccion: null`).
  const etapa2Resultado = etapa2
    ? {
        ranking: etapa2.ranking,
        warnings: etapa2.warnings,
        puntos_empiricos: etapa2.puntos_empiricos,
        seleccion: null,
      }
    : null;

  return (
    <div className="results-page">
      <h1 className="h">Resultados de Etapa 1</h1>
      <Etapa1ResultView
        result={result}
        modo={modoEfectivo}
        mesInicioAnio={locationState?.mesInicioAnio}
      />
      {/* Etapa 2 ya corrió dentro del stream (StreamPage) si el usuario la
          pidió al configurar el análisis. Si no se pidió Etapa 2, no hay
          nada que mostrar acá — ver DECISIÓN 052/054. Con `analysisId`
          (CU-01) el ranking se puede explorar; sin él (CU-02) es de solo
          lectura, sin botones "Elegir". */}
      {etapa2Resultado && (
        <div style={{ marginTop: 20 }}>
          <h2 className="h" style={{ fontSize: 16, marginBottom: 0 }}>
            Ranking de distribuciones
          </h2>
          {analysisId ? (
            <Etapa2Explorador
              etapa2={etapa2Resultado}
              explorar={(distribucion, metodo, periodosRetorno) =>
                postRecalcularDesignEvents(analysisId, {
                  distribucion,
                  metodo,
                  periodos_retorno: periodosRetorno,
                })
              }
              mediaSerie={result.descriptive?.media}
              seleccionRegistrada={eventosDiseno}
            />
          ) : (
            <Etapa2RankingView
              etapa2={etapa2Resultado}
              modo="lectura"
              mediaSerie={result.descriptive?.media}
            />
          )}
        </div>
      )}
      {eventosDiseno && (
        <div style={{ marginTop: 20 }}>
          <h2 className="h" style={{ fontSize: 16, marginBottom: 0 }}>
            Evento de diseño
          </h2>
          <Etapa2EventosView
            eventos={eventosDiseno}
            puntosEmpiricos={etapa2?.puntos_empiricos ?? []}
          />
        </div>
      )}
    </div>
  );
}
