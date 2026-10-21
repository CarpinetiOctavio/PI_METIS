import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type {
  Etapa1Datos,
  Etapa1Result,
  SimulateExclusionResponse,
  TestResultDetail,
} from "../../api/types";
import { Etapa1BoxplotMensualChart } from "./Etapa1BoxplotMensualChart";
import { Etapa1ChowChart } from "./Etapa1ChowChart";
import { Etapa1Comparacion } from "./Etapa1Comparacion";
import { Etapa1ExclusionPanel } from "./Etapa1ExclusionPanel";
import { Etapa1SerieTemporalChart } from "./Etapa1SerieTemporalChart";
import { claveSeleccion, puntosDeSerie } from "./exclusiones";
import type { ExclusionesGuardables } from "./exclusiones";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import { useSimulacionExclusion } from "./useSimulacionExclusion";
import type { SimularFn } from "./useSimulacionExclusion";

/**
 * Gráficos de Etapa 1 (serie temporal, Chow, boxplot mensual) más el panel de
 * exclusión de puntos. Es el dueño del estado de la selección: la comparten los
 * dos gráficos con eje de año (clic sobre un punto) y la lista con checkbox del
 * panel, así que tiene que vivir por encima de los tres. `Etapa1ResultView`
 * sigue siendo presentacional puro.
 *
 * Los índices de la selección son posiciones en `datos.serie_efectiva` — el
 * mismo espacio que `datos.indice_atipico`.
 */
export function Etapa1GraficosView({
  datos,
  chow,
  mesInicioAnio,
  nombreArchivo,
  resultado,
  simular,
  onSimulacionVigente,
  tipoVariable,
  exclusiones,
}: Readonly<{
  datos: Etapa1Datos;
  chow?: TestResultDetail;
  mesInicioAnio?: number;
  // Para el texto de Chow no ejecutada: "físicamente imposible" solo en caudal.
  tipoVariable?: string;
  nombreArchivo?: string | null;
  // A2 — el resultado original (para compararlo) y cómo pedir el simulado. Sin
  // `simular` no hay botón de recalcular: queda la exclusión de A1.
  resultado?: Etapa1Result;
  simular?: SimularFn;
  // La simulación que corresponde a la selección actual, o null si no hay o
  // quedó desactualizada. La página la usa para los eventos de diseño del fondo.
  onSimulacionVigente?: (simulacion: SimulateExclusionResponse | null) => void;
  // DECISIÓN 080 — solo CU-01 (análisis persistido): guardar la exclusión de la
  // comparación vigente y, desde el historial, cargar una guardada.
  exclusiones?: ExclusionesGuardables;
}>) {
  const [excluidos, setExcluidos] = useState<ReadonlySet<number>>(new Set());
  const puntos = useMemo(() => puntosDeSerie(datos), [datos]);

  const alternar = useCallback((indice: number) => {
    setExcluidos((previos) => {
      const siguientes = new Set(previos);
      if (!siguientes.delete(indice)) siguientes.add(indice);
      return siguientes;
    });
  }, []);
  const { estado: simulacion, calcular, reiniciar } = useSimulacionExclusion(simular);

  const limpiar = useCallback(() => {
    setExcluidos(new Set());
    reiniciar();
  }, [reiniciar]);

  // "Ver" una exclusión guardada (DECISIÓN 080): carga la selección y simula.
  // Una sola vez por pedido — `calcular` cambia de identidad en cada render de
  // la página (simular se arma ahí), así que no puede gatillar el efecto solo.
  const cargar = exclusiones?.cargar;
  const ultimoCargado = useRef<number | null>(null);
  useEffect(() => {
    if (!cargar || cargar.pedido === ultimoCargado.current) return;
    ultimoCargado.current = cargar.pedido;
    const indices = new Set(cargar.indices);
    setExcluidos(indices);
    void calcular(indices);
  }, [cargar, calcular]);

  const seleccion = { excluidos, onToggle: alternar };
  const simulacionVigente =
    simulacion.fase === "lista" && mismaSeleccion(simulacion.indices, excluidos)
      ? simulacion.respuesta
      : null;

  useEffect(() => {
    onSimulacionVigente?.(simulacionVigente);
  }, [simulacionVigente, onSimulacionVigente]);

  return (
    <div className="stack" style={{ marginTop: 14 }}>
      <Etapa1SerieTemporalChart datos={datos} seleccion={seleccion} mesInicioAnio={mesInicioAnio} />
      <Etapa1ChowChart
        datos={datos}
        chow={chow}
        mesInicioAnio={mesInicioAnio}
        seleccion={seleccion}
        tipoVariable={tipoVariable}
      />
      {puntos.length > 0 && (
        <Etapa1ExclusionPanel
          puntos={puntos}
          excluidos={excluidos}
          onToggle={alternar}
          onLimpiar={limpiar}
          sugeridos={
            chow?.valores_atipicos
              ? chow.valores_atipicos.map((a) => a.indice)
              : datos.indice_atipico !== null
                ? [datos.indice_atipico]
                : []
          }
          noValidos={
            chow?.veredicto === "no_ejecutada"
              ? (chow.valores_no_validos ?? []).map((v) => v.indice)
              : []
          }
          resolucionOriginal={datos.resolucion_original}
          nombreArchivo={nombreArchivo}
          onRecalcular={simular && resultado ? () => calcular(excluidos) : undefined}
          calculando={simulacion.fase === "calculando"}
          errorSimulacion={simulacion.fase === "error" ? simulacion.mensaje : null}
          serieResultante={simulacionVigente ?? undefined}
        />
      )}
      {resultado && simulacion.fase === "lista" && (
        <Etapa1Comparacion
          original={resultado}
          simulacion={simulacion.respuesta}
          desactualizada={!mismaSeleccion(simulacion.indices, excluidos)}
        />
      )}
      {exclusiones && simulacionVigente && simulacion.fase === "lista" && (
        <GuardarExclusion indices={simulacion.indices} exclusiones={exclusiones} />
      )}
      <Etapa1BoxplotMensualChart datos={datos} mesInicioAnio={mesInicioAnio} />
    </div>
  );
}

function mismaSeleccion(indices: readonly number[], excluidos: ReadonlySet<number>): boolean {
  return indices.length === excluidos.size && indices.every((i) => excluidos.has(i));
}

/**
 * DECISIÓN 080 — guarda la exclusión de la comparación vigente en el historial,
 * aparte del resultado (no lo modifica: DECISIÓN 062). Solo a pedido: una
 * exclusión probada y descartada no queda registrada. Ya guardada, lo dice y no
 * vuelve a ofrecerse para la misma selección.
 */
function GuardarExclusion({
  indices,
  exclusiones,
}: Readonly<{ indices: readonly number[]; exclusiones: ExclusionesGuardables }>) {
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (exclusiones.guardadas.has(claveSeleccion(indices))) {
    return (
      <p className="fn" role="status">
        Guardada: esta exclusión figura en el historial del análisis.
      </p>
    );
  }

  async function guardar() {
    setGuardando(true);
    setError(null);
    try {
      await exclusiones.guardar([...indices]);
    } catch (err) {
      setError(err instanceof ApiError ? errorText(err.codigo) : errorText(""));
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div className="row" style={{ alignItems: "center", gap: 10 }}>
      <button type="button" className="b b-sec" disabled={guardando} onClick={guardar}>
        Guardar esta exclusión en el historial
      </button>
      {error && (
        <span className="fn" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
