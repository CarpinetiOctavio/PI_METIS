import { useCallback, useRef, useState } from "react";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import type { SimulateExclusionResponse } from "../../api/types";

/** Pide el resultado de Etapa 1 (y 2) sin los puntos de `indices`. La página
 * que monta la vista lo arma con la configuración del análisis; la vista solo
 * sabe qué índices quiere excluir. */
export type SimularFn = (indicesExcluidos: number[]) => Promise<SimulateExclusionResponse>;

export type SimulacionEstado =
  | { fase: "ninguna" }
  | { fase: "calculando" }
  | { fase: "error"; mensaje: string }
  | { fase: "lista"; indices: number[]; respuesta: SimulateExclusionResponse };

/**
 * Estado del what-if. Es efímero a propósito (DECISIÓN 062, "explorar no es
 * decidir"): no se persiste ni toca el análisis original.
 *
 * Si el usuario vuelve a pedir un cálculo antes de que llegue el anterior, solo
 * cuenta el último — una respuesta vieja que llega tarde no pisa a la nueva.
 */
export function useSimulacionExclusion(simular: SimularFn | undefined) {
  const [estado, setEstado] = useState<SimulacionEstado>({ fase: "ninguna" });
  const ultimoPedido = useRef(0);

  const calcular = useCallback(
    async (indices: ReadonlySet<number>) => {
      if (!simular) return;
      const pedido = ++ultimoPedido.current;
      const ordenados = [...indices].sort((a, b) => a - b);
      setEstado({ fase: "calculando" });
      try {
        const respuesta = await simular(ordenados);
        if (pedido === ultimoPedido.current) {
          setEstado({ fase: "lista", indices: ordenados, respuesta });
        }
      } catch (err) {
        if (pedido === ultimoPedido.current) {
          setEstado({
            fase: "error",
            mensaje: err instanceof ApiError ? errorText(err.codigo) : errorText(""),
          });
        }
      }
    },
    [simular],
  );

  const reiniciar = useCallback(() => {
    ultimoPedido.current++; // descarta lo que esté en vuelo
    setEstado({ fase: "ninguna" });
  }, []);

  return { estado, calcular, reiniciar };
}
