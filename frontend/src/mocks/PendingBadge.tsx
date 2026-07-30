import "./PendingBadge.css";

/**
 * Marca visual de que la pantalla usa datos de ejemplo, no una respuesta
 * real del backend — ver docs/frontend/frontend-implementation-plan.md §6.
 */
export function PendingBadge({ note }: Readonly<{ note?: string }>) {
  // D10 (pasada de mejora): `title` es un tooltip de mouse, no un afordance
  // confiable ni para teclado ni para lector de pantalla. La nota ahora
  // también existe como texto real (visualmente oculto con .visually-hidden,
  // no con title) para que forme parte del nombre accesible del elemento.
  const text = note ?? "Etapa 2 no expuesta por API todavía — datos de ejemplo";
  return (
    <span className="tag pending-badge" title={text}>
      pendiente · datos de ejemplo
      <span className="visually-hidden">{`— ${text}`}</span>
    </span>
  );
}
