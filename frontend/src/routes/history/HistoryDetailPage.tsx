import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getHistoryItem } from "../../api/history";
import { postRecalcularDesignEvents } from "../../api/analysis";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import { Etapa1ResultView } from "../results/Etapa1ResultView";
import { Etapa2Explorador } from "../results/Etapa2Explorador";
import { Etapa2EventosView } from "../results/Etapa2EventosView";
import { ExportarPdfButton } from "../results/ExportarPdfButton";
import { DecisionesChowView } from "./DecisionesChowView";
import type {
  AnalysisDetail,
  Modo,
  SimulateExclusionResponse,
  TipoVariable,
} from "../../api/types";
import { crearPedirSimulacion, crearSimular } from "../results/simulacion";
import type { ContextoSerie } from "../../i18n/periodoRetorno";
import "./HistoryDetailPage.css";

export function HistoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Bloque B (revisión manual 21/10/2026): la simulación vigente, para ofrecer el
  // PDF con los resultados sin esos puntos. No se guarda (DECISIÓN 062).
  const [simulacion, setSimulacion] = useState<SimulateExclusionResponse | null>(null);
  const alCambiarSimulacion = useCallback(
    (nueva: SimulateExclusionResponse | null) => setSimulacion(nueva),
    [],
  );

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
  // DECISIÓN 076: qué se cargó y con qué año se agregó, para rotular T.
  const contextoSerie: ContextoSerie = {
    resolucion: detail.etapa1?.datos?.resolucion_original,
    mesInicioAnio: detail.configuracion?.mes_inicio_anio,
    variableDiaria: detail.configuracion?.variable_diaria,
  };
  // Bloque B (revisión manual 21/10/2026) — el what-if de atípicos con los datos
  // persistidos: la serie analizada, el tipo de variable, la partición, el α y la
  // elección registrada. Un análisis anterior a la DECISIÓN 058 no tiene los años
  // de la serie (`timestamps === null`): ahí no hay simulación (ver el aviso).
  const pedirSimulacion = crearPedirSimulacion(
    detail.timestamps === null ? undefined : detail.etapa1?.datos,
    esTipoVariable(detail.tipo_variable)
      ? {
          tipoVariable: detail.tipo_variable,
          cramerParticion: detail.configuracion?.cramer_particion,
          conEtapa2: detail.etapas?.includes("2") ?? false,
          alfa: detail.configuracion?.alfa ?? detail.etapa1?.alfa ?? 0.05,
        }
      : null,
  );
  const simular = crearSimular(
    pedirSimulacion,
    seleccion && {
      distribucion: seleccion.distribucion,
      metodo: seleccion.metodo,
      periodos_retorno: seleccion.periodos_retorno,
    },
  );

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
        contextoSerie={contextoSerie}
      />
    </>
  );

  return (
    <div className="history-detail-page">
      <div className="encabezado-exportable">
        <h1 className="h">Detalle del análisis</h1>
        <ExportarPdfButton
          analysisId={detail.id}
          indicesExcluidos={simulacion?.excluidos.map((e) => e.indice)}
        />
      </div>
      <p className="sub">
        {detail.tipo_variable} · {new Date(detail.created_at).toLocaleString("es-AR")}
      </p>
      <DecisionesChowView chow={detail.decisiones?.chow} />
      {detail.etapa1 ? (
        <>
          <Etapa1ResultView
            result={detail.etapa1}
            modo={(detail.modo as Modo | null) ?? "experto"}
            mesInicioAnio={detail.configuracion?.mes_inicio_anio}
            nombreArchivo={detail.configuracion?.nombre_archivo}
            tipoVariable={detail.tipo_variable}
            cramerParticion={detail.configuracion?.cramer_particion}
            simular={simular}
            onSimulacionVigente={alCambiarSimulacion}
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
              antigüedad, y tampoco la simulación sin puntos excluidos: no
              quedaron registrados los años de la serie analizada.
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
            contextoSerie={contextoSerie}
            eleccion={eleccionRegistrada}
          />
        </div>
      )}
    </div>
  );
}

function esTipoVariable(valor: string): valor is TipoVariable {
  return valor === "caudal_precipitacion" || valor === "otro";
}
