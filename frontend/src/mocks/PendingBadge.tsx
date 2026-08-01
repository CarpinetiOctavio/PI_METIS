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
  // F1 (pasada 4, plan-mejora-frontend-pasada4.md): el texto anterior
  // ("pendiente · datos de ejemplo") no dejaba claro si "pendiente" se
  // refería al análisis del usuario o a la feature — se reformula para que
  // quede inequívoco que Etapa 2 en sí es lo que falta, no el resultado.
  const text =
    note ??
    "Esta pantalla muestra un ejemplo de cómo se presentarán los resultados. El análisis de frecuencia todavía no se calcula sobre tus datos.";
  return (
    <span className="tag pending-badge" title={text}>
      {"Vista previa · datos de demostración"}
      <span className="visually-hidden">{`— ${text}`}</span>
    </span>
  );
}
