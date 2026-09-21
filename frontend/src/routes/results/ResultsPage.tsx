import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import {
  postRecalcularDesignEvents,
  postSimularExclusion,
  simulacionExclusionDisponible,
} from "../../api/analysis";
import { Etapa1ResultView } from "./Etapa1ResultView";
import { Etapa2Explorador } from "./Etapa2Explorador";
import { Etapa2RankingView } from "./Etapa2RankingView";
import { Etapa2EventosView } from "./Etapa2EventosView";
import type { CramerParticion, Etapa1Result, Modo, TipoVariable } from "../../api/types";
import type { SimularFn } from "./useSimulacionExclusion";
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
  // Nombre del archivo subido — nombra el CSV de la serie sin los puntos excluidos.
  nombreArchivo?: string;
  // Configuración con la que se corrió el análisis — la necesita el what-if de
  // atípicos para repetirlo sobre la serie sin los puntos excluidos.
  tipoVariable?: TipoVariable;
  cramerParticion?: CramerParticion;
  etapas?: "1" | "1,2";
}

// El backend recibe la partición de Cramer como texto: "default" o el objeto en
// JSON, igual que en POST /analysis/stream (api/sse.ts::buildFormData).
function cramerParticionComoTexto(particion: CramerParticion | undefined): string {
  if (particion === undefined) return "default";
  return typeof particion === "string" ? particion : JSON.stringify(particion);
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
  // Con `analysisId` el "Evento de diseño" (la elección del stream) se muestra
  // junto a la exploración, dentro de Etapa2Explorador, para compararlas; sin
  // él (CU-02) se muestra aparte, debajo del ranking de solo lectura.
  const explorable = Boolean(etapa2Resultado && analysisId);
  const eventoDiseno = eventosDiseno && (
    <>
      <h2 className="h" style={{ fontSize: 16, marginBottom: 0 }}>
        Evento de diseño
      </h2>
      <Etapa2EventosView
        eventos={eventosDiseno}
        puntosEmpiricos={etapa2?.puntos_empiricos ?? []}
      />
    </>
  );

  // What-if de atípicos (ítem A): solo con la configuración a mano y con el
  // endpoint disponible en el backend (todavía no lo está, ver api/analysis.ts).
  const datos = result.datos;
  const tipoVariable = locationState?.tipoVariable;
  const simular: SimularFn | undefined =
    simulacionExclusionDisponible() && datos?.timestamps_efectivos && tipoVariable
      ? (indicesExcluidos) =>
          postSimularExclusion({
            serie: datos.serie_efectiva,
            anios: datos.timestamps_efectivos!.map((t) => t.anio),
            tipo_variable: tipoVariable,
            cramer_particion: cramerParticionComoTexto(locationState?.cramerParticion),
            indices_excluidos: indicesExcluidos,
            etapas: locationState?.etapas === "1,2" ? [1, 2] : [1],
          })
      : undefined;

  return (
    <div className="results-page">
      <h1 className="h">Resultados de Etapa 1</h1>
      <Etapa1ResultView
        result={result}
        modo={modoEfectivo}
        mesInicioAnio={locationState?.mesInicioAnio}
        nombreArchivo={locationState?.nombreArchivo}
        simular={simular}
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
          {explorable && analysisId ? (
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
              eleccion={eventoDiseno}
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
      {!explorable && eventoDiseno && <div style={{ marginTop: 20 }}>{eventoDiseno}</div>}
    </div>
  );
}
