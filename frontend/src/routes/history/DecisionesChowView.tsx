import type { DecisionesChow } from "../../api/types";
import { formatNum } from "../../i18n/format";

/**
 * Bloque C1 de la revisión manual del 21/10/2026 (D-16, #138). Lo que el
 * usuario decidió en la pausa de Chow, leído de `decisiones.chow`. Sin esto la
 * serie del historial se veía más corta sin explicación: el análisis guardado
 * es el de la serie sin los rechazados. Lee las dos formas del registro, como
 * el PDF (`reportes/pdf.py`): la de DECISIÓN 079, una fila por punto, y la
 * anterior, un solo dato.
 */
export function DecisionesChowView({ chow }: Readonly<{ chow: DecisionesChow | undefined }>) {
  if (!chow) return null;

  if (!("atipicos" in chow)) {
    const rechazado = chow.accion === "rechazar";
    return (
      <section className="card decisiones-chow" aria-labelledby="decisiones-chow-titulo">
        <h2 id="decisiones-chow-titulo" className="h" style={{ fontSize: 14 }}>
          Decisión ante el atípico de Chow
        </h2>
        <p className="sub">
          Dato {formatNum(chow.dato)}:{" "}
          {rechazado
            ? "rechazado y excluido del análisis. Los resultados guardados corresponden a la serie sin ese dato."
            : "aceptado como parte de la población."}
        </p>
      </section>
    );
  }

  const rechazados = chow.atipicos.filter((a) => a.decision === "rechazar").length;
  return (
    <section className="card decisiones-chow" aria-labelledby="decisiones-chow-titulo">
      <h2 id="decisiones-chow-titulo" className="h" style={{ fontSize: 14 }}>
        Decisiones ante Chow
      </h2>
      {rechazados > 0 && (
        <p className="sub">
          Los resultados guardados corresponden a la serie sin{" "}
          {rechazados === 1 ? "el punto rechazado" : `los ${rechazados} puntos rechazados`}.
        </p>
      )}
      <table className="t">
        <thead>
          <tr>
            <th>Año</th>
            <th>Valor</th>
            <th>Lado</th>
            <th>Desvíos</th>
            <th>Decisión</th>
          </tr>
        </thead>
        <tbody>
          {chow.atipicos.map((a) => (
            <tr key={a.indice}>
              <td>{a.periodo ?? "—"}</td>
              <td className="num">{formatNum(a.valor)}</td>
              <td>{a.lado === "alto" ? "Alto" : "Bajo"}</td>
              <td className="num">{formatNum(Math.abs(a.z))}</td>
              <td>
                {a.decision === "rechazar"
                  ? "Rechazado: excluido del análisis"
                  : "Aceptado como parte de la población"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
