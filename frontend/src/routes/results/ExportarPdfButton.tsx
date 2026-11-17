import { useState } from "react";
import { guardarPdf, obtenerPdfAnalisis } from "../../api/export";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import "./ExportarPdfButton.css";

interface ExportarPdfButtonProps {
  analysisId: string;
  /** Puntos excluidos de la simulación vigente (DECISIÓN 071), como posiciones en
   * `datos.serie_efectiva`. Con al menos uno aparece "Exportar PDF con la
   * simulación", que suma al informe los resultados sin esos puntos. */
  indicesExcluidos?: readonly number[];
}

type Exportacion = "analisis" | "simulacion";

/** Exporta el análisis persistido a PDF (DECISIÓN 075). Solo CU-01: quien lo
 * monta decide si hay sesión y `analysisId`. El PDF es siempre formato Experto,
 * sea cual sea el modo en que se está viendo el análisis. */
export function ExportarPdfButton({ analysisId, indicesExcluidos }: ExportarPdfButtonProps) {
  const [generando, setGenerando] = useState<Exportacion | null>(null);
  const [error, setError] = useState<string | null>(null);
  const conSimulacion = Boolean(indicesExcluidos?.length);

  async function exportar(tipo: Exportacion) {
    setGenerando(tipo);
    setError(null);
    try {
      guardarPdf(
        await obtenerPdfAnalisis(analysisId, tipo === "simulacion" ? indicesExcluidos : undefined),
      );
    } catch (err) {
      setError(err instanceof ApiError ? errorText(err.codigo) : errorText(""));
    } finally {
      setGenerando(null);
    }
  }

  return (
    <div className="exportar-pdf">
      <div className="exportar-pdf__botones">
        <button
          type="button"
          className="b b-sec"
          onClick={() => void exportar("analisis")}
          disabled={generando !== null}
          aria-busy={generando === "analisis"}
        >
          {generando === "analisis" ? "Generando PDF…" : "Exportar PDF"}
        </button>
        {conSimulacion && (
          <button
            type="button"
            className="b b-sec"
            onClick={() => void exportar("simulacion")}
            disabled={generando !== null}
            aria-busy={generando === "simulacion"}
          >
            {generando === "simulacion" ? "Generando PDF…" : "Exportar PDF con la simulación"}
          </button>
        )}
      </div>
      {error && (
        <div className="banner crit" role="alert">
          <span className="ic">!</span> No se pudo exportar el PDF: {error}
        </div>
      )}
    </div>
  );
}
