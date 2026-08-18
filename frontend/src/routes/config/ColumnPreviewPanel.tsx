import type { ColumnaPreview } from "../../api/types";
import type { PanelDock } from "./useColumnPanelDock";
import "./ColumnPreviewPanel.css";

// Bloque E3 (pasada 5) — presentacional puro, sin estado propio ni llamadas
// de red, misma disciplina que Etapa1ResultView.tsx (Fase 3 del frontend).
// Bloque E (plan post-avance) — gana cerrar/reabrir y el selector de acople;
// la posición y el tamaño en sí los decide y persiste ConfigPage (vía
// useColumnPanelDock), este componente solo refleja el dock actual.
interface ColumnPreviewPanelProps {
  columnas: ColumnaPreview[];
  filas: number;
  // Índice de columna como string, o null si ninguna está resaltada —
  // mismo tipo que el value de los <select> en ConfigPage.
  columnaResaltada: string | null;
  dock: PanelDock;
  onDockChange: (dock: PanelDock) => void;
  onClose: () => void;
}

const FILAS_DE_MUESTRA = 3;

const DOCKS: Array<{ value: PanelDock; etiqueta: string }> = [
  { value: "right", etiqueta: "Derecha" },
  { value: "left", etiqueta: "Izquierda" },
  { value: "bottom", etiqueta: "Abajo" },
];

export function ColumnPreviewPanel({
  columnas,
  filas,
  columnaResaltada,
  dock,
  onDockChange,
  onClose,
}: ColumnPreviewPanelProps) {
  function claseColumna(indice: number): string {
    return String(indice) === columnaResaltada
      ? "column-preview-panel__col--activa"
      : "";
  }

  return (
    <div className="card column-preview-panel">
      <div className="column-preview-panel__header">
        <p className="ct" style={{ marginBottom: 0 }}>
          Vista previa de columnas
        </p>
        <div className="column-preview-panel__header-actions">
          <div className="seg column-preview-panel__dock" role="group" aria-label="Posición del panel">
            {DOCKS.map((opcion) => (
              <button
                key={opcion.value}
                type="button"
                className={dock === opcion.value ? "on" : ""}
                aria-pressed={dock === opcion.value}
                onClick={() => onDockChange(opcion.value)}
              >
                {opcion.etiqueta}
              </button>
            ))}
          </div>
          <button
            type="button"
            className="column-preview-panel__close"
            aria-label="Cerrar panel de columnas"
            onClick={onClose}
          >
            ×
          </button>
        </div>
      </div>
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
