import type { ColumnaPreview } from "../../api/types";
import "./ColumnPreviewPanel.css";

// Bloque E3 (pasada 5) — presentacional puro, sin estado propio ni llamadas
// de red, misma disciplina que Etapa1ResultView.tsx (Fase 3 del frontend).
interface ColumnPreviewPanelProps {
  columnas: ColumnaPreview[];
  filas: number;
  // Índice de columna como string, o null si ninguna está resaltada —
  // mismo tipo que el value de los <select> en ConfigPage.
  columnaResaltada: string | null;
}

const FILAS_DE_MUESTRA = 3;

export function ColumnPreviewPanel({
  columnas,
  filas,
  columnaResaltada,
}: ColumnPreviewPanelProps) {
  function claseColumna(indice: number): string {
    return String(indice) === columnaResaltada
      ? "column-preview-panel__col--activa"
      : "";
  }

  return (
    <div className="card column-preview-panel">
      <p className="ct">Vista previa de columnas</p>
      <div className="column-preview-panel__scroll">
        <table className="column-preview-panel__table">
          <thead>
            <tr>
              {columnas.map((col) => (
                <th key={col.indice} className={claseColumna(col.indice)}>
                  {col.nombre}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: FILAS_DE_MUESTRA }, (_, fila) => (
              <tr key={fila}>
                {columnas.map((col) => (
                  <td key={col.indice} className={claseColumna(col.indice)}>
                    {col.muestra[fila] ?? ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="fn">{filas} filas en el archivo</p>
    </div>
  );
}
