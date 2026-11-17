import { apiFetch, toApiError } from "./client";

const NOMBRE_POR_DEFECTO = "metis_analisis.pdf";

export interface PdfAnalisis {
  blob: Blob;
  nombre: string;
}

function nombreDesdeContentDisposition(header: string | null): string {
  return header?.match(/filename="([^"]+)"/)?.[1] ?? NOMBRE_POR_DEFECTO;
}

/** Informe PDF, en formato Experto, de un análisis persistido (DECISIÓN 075). Solo
 * CU-01: requiere la cookie de sesión.
 *
 * Sin `indicesExcluidos`: `GET /api/v1/export/{id}`, el análisis registrado. Con
 * ellos: `POST /api/v1/export/{id}/simulacion`, que agrega los resultados sin esos
 * puntos (DECISIÓN 071) — el backend los recalcula desde el análisis guardado; del
 * cliente solo viajan las posiciones en `datos.serie_efectiva`. */
export async function obtenerPdfAnalisis(
  id: string,
  indicesExcluidos?: readonly number[],
): Promise<PdfAnalisis> {
  const response = indicesExcluidos?.length
    ? await apiFetch(`/api/v1/export/${id}/simulacion`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ indices_excluidos: indicesExcluidos }),
      })
    : await apiFetch(`/api/v1/export/${id}`);
  if (!response.ok) {
    throw await toApiError(response);
  }
  return {
    blob: await response.blob(),
    nombre: nombreDesdeContentDisposition(response.headers.get("Content-Disposition")),
  };
}

/** Guarda el PDF en el equipo. Separado de `obtenerPdfAnalisis` para poder
 * reemplazarlo en los tests: jsdom no implementa `URL.createObjectURL`. */
export function guardarPdf({ blob, nombre }: PdfAnalisis): void {
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = nombre;
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();
  URL.revokeObjectURL(url);
}
