import { useCallback, useMemo, useState } from "react";
import type { Etapa1Datos, TestResultDetail } from "../../api/types";
import { Etapa1BoxplotMensualChart } from "./Etapa1BoxplotMensualChart";
import { Etapa1ChowChart } from "./Etapa1ChowChart";
import { Etapa1ExclusionPanel } from "./Etapa1ExclusionPanel";
import { Etapa1SerieTemporalChart } from "./Etapa1SerieTemporalChart";
import { puntosDeSerie } from "./exclusiones";

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
}: Readonly<{
  datos: Etapa1Datos;
  chow?: TestResultDetail;
  mesInicioAnio?: number;
  nombreArchivo?: string | null;
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
  const limpiar = useCallback(() => setExcluidos(new Set()), []);

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
        />
      )}
      <Etapa1BoxplotMensualChart datos={datos} mesInicioAnio={mesInicioAnio} />
    </div>
  );
}
