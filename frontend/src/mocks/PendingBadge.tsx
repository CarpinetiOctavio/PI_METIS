import "./PendingBadge.css";

/**
 * Marca visual de que la pantalla usa datos de ejemplo, no una respuesta
 * real del backend — ver frontend-implementation-plan.md §6.
 */
export function PendingBadge({ note }: { note?: string }) {
  return (
    <span
      className="tag pending-badge"
      title={note ?? "Etapa 2 no expuesta por API todavía — datos de ejemplo"}
    >
      pendiente · datos de ejemplo
    </span>
  );
}
