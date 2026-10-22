import { postSimularExclusion } from "../../api/analysis";
import type {
  Alfa,
  CramerParticion,
  Etapa1Datos,
  SimulateExclusionRequest,
  SimulateExclusionResponse,
  TipoVariable,
} from "../../api/types";
import type { SimularFn } from "./useSimulacionExclusion";

/**
 * What-if de atípicos (DECISIÓN 071), compartido por Resultados y el detalle del
 * historial (bloque B de la revisión manual del 21/10/2026). Las dos páginas
 * arman el mismo pedido a `POST /analysis/simulate-exclusion`: Resultados con la
 * configuración que viaja en el router state, el historial con la persistida.
 * La simulación no se guarda ni toca el registro (DECISIÓN 062).
 */

export type Seleccion = NonNullable<SimulateExclusionRequest["seleccion"]>;

export type PedirSimulacion = (
  indicesExcluidos: number[],
  seleccion?: Seleccion,
) => Promise<SimulateExclusionResponse>;

export interface ConfiguracionSimulacion {
  tipoVariable: TipoVariable;
  cramerParticion: CramerParticion | undefined;
  conEtapa2: boolean;
  alfa: Alfa;
}

// El backend recibe la partición de Cramer como texto: "default" o el objeto en
// JSON, igual que en POST /analysis/stream (api/sse.ts::buildFormData).
export function cramerParticionComoTexto(particion: CramerParticion | undefined): string {
  if (particion === undefined) return "default";
  return typeof particion === "string" ? particion : JSON.stringify(particion);
}

/** Sin la serie analizada con sus años (análisis anterior a la DECISIÓN 058) o
 * sin la configuración, no hay simulación posible: `undefined`. */
export function crearPedirSimulacion(
  datos: Etapa1Datos | undefined,
  configuracion: ConfiguracionSimulacion | null,
): PedirSimulacion | undefined {
  const timestamps = datos?.timestamps_efectivos;
  if (!datos || !timestamps || !configuracion) return undefined;
  return (indicesExcluidos, seleccion) =>
    postSimularExclusion({
      serie: datos.serie_efectiva,
      anios: timestamps.map((t) => t.anio),
      tipo_variable: configuracion.tipoVariable,
      cramer_particion: cramerParticionComoTexto(configuracion.cramerParticion),
      indices_excluidos: indicesExcluidos,
      etapas: configuracion.conEtapa2 ? [1, 2] : [1],
      // DECISIÓN 078 — la simulación compara contra el mismo α.
      alfa: configuracion.alfa,
      ...(seleccion && { seleccion }),
    });
}

/** Con la elección registrada, el backend recalcula también sus eventos de
 * diseño sin los puntos excluidos. */
export function crearSimular(
  pedir: PedirSimulacion | undefined,
  seleccion: Seleccion | null | undefined,
): SimularFn | undefined {
  return pedir && ((indicesExcluidos) => pedir(indicesExcluidos, seleccion ?? undefined));
}
