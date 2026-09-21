import { useCallback, useMemo, useState } from "react";
import type { Etapa1Datos, Etapa1Result, TestResultDetail } from "../../api/types";
import { Etapa1BoxplotMensualChart } from "./Etapa1BoxplotMensualChart";
import { Etapa1ChowChart } from "./Etapa1ChowChart";
import { Etapa1Comparacion } from "./Etapa1Comparacion";
import { Etapa1ExclusionPanel } from "./Etapa1ExclusionPanel";
import { Etapa1SerieTemporalChart } from "./Etapa1SerieTemporalChart";
import { puntosDeSerie } from "./exclusiones";
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
}: Readonly<{
  datos: Etapa1Datos;
  chow?: TestResultDetail;
  mesInicioAnio?: number;
  nombreArchivo?: string | null;
  // A2 — el resultado original (para compararlo) y cómo pedir el simulado. Sin
  // `simular` no hay botón de recalcular: queda la exclusión de A1.
  resultado?: Etapa1Result;
  simular?: SimularFn;
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

  const seleccion = { excluidos, onToggle: alternar };

  return (
    <div className="stack" style={{ marginTop: 14 }}>
      <Etapa1SerieTemporalChart datos={datos} seleccion={seleccion} />
      <Etapa1ChowChart
        datos={datos}
        chow={chow}
        mesInicioAnio={mesInicioAnio}
        seleccion={seleccion}
      />
      {puntos.length > 0 && (
        <Etapa1ExclusionPanel
          puntos={puntos}
          excluidos={excluidos}
          onToggle={alternar}
          onLimpiar={limpiar}
          sugerido={datos.indice_atipico}
          resolucionOriginal={datos.resolucion_original}
          nombreArchivo={nombreArchivo}
          onRecalcular={simular && resultado ? () => calcular(excluidos) : undefined}
          calculando={simulacion.fase === "calculando"}
          errorSimulacion={simulacion.fase === "error" ? simulacion.mensaje : null}
        />
      )}
      {resultado && simulacion.fase === "lista" && (
        <Etapa1Comparacion
          original={resultado}
          simulacion={simulacion.respuesta}
          desactualizada={!mismaSeleccion(simulacion.indices, excluidos)}
        />
      )}
      <Etapa1BoxplotMensualChart datos={datos} mesInicioAnio={mesInicioAnio} />
    </div>
  );
}

function mismaSeleccion(indices: readonly number[], excluidos: ReadonlySet<number>): boolean {
  return indices.length === excluidos.size && indices.every((i) => excluidos.has(i));
}
