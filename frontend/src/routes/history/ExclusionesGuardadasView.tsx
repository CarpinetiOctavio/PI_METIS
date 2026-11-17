import type { ExclusionGuardada } from "../../api/types";

/**
 * DECISIÓN 080 — las exclusiones de puntos guardadas sobre este análisis. Cada
 * una con su fecha y sus años; "Ver" la carga en el panel de exclusión y
 * recalcula la comparación (el resultado no se guarda, se recalcula); "Quitar"
 * la borra. Ninguna de las dos toca el resultado ni las decisiones del análisis.
 * Los dos botones con el mismo peso: el frontend no sugiere qué hacer.
 */
export function ExclusionesGuardadasView({
  exclusiones,
  onVer,
  onQuitar,
  quitando,
  error,
}: Readonly<{
  exclusiones: ExclusionGuardada[];
  onVer: (exclusion: ExclusionGuardada) => void;
  onQuitar: (exclusion: ExclusionGuardada) => void;
  quitando: string | null;
  error: string | null;
}>) {
  if (exclusiones.length === 0) return null;
  return (
    <section className="card exclusiones-guardadas" aria-labelledby="exclusiones-guardadas-titulo">
      <h2 id="exclusiones-guardadas-titulo" className="h" style={{ fontSize: 14 }}>
        Exclusiones guardadas
      </h2>
      <p className="sub">
        Exploraciones guardadas sobre este análisis. No cambian sus resultados ni sus decisiones:
        al verlas, los resultados sin esos puntos se vuelven a calcular.
      </p>
      <ul className="stack exclusiones-guardadas-lista">
        {exclusiones.map((e) => {
          const anios = e.puntos.map((p) => p.periodo ?? `posición ${p.indice + 1}`).join(", ");
          return (
            <li key={e.id} className="row" style={{ alignItems: "center", gap: 10 }}>
              <span>
                Sin {anios}{" "}
                <span className="fn">· {new Date(e.creado_at).toLocaleString("es-AR")}</span>
              </span>
              <span className="sp" />
              <button
                type="button"
                className="b b-sec"
                aria-label={`Ver la exclusión sin ${anios}`}
                onClick={() => onVer(e)}
              >
                Ver
              </button>
              <button
                type="button"
                className="b b-sec"
                aria-label={`Quitar la exclusión sin ${anios}`}
                disabled={quitando === e.id}
                onClick={() => onQuitar(e)}
              >
                Quitar
              </button>
            </li>
          );
        })}
      </ul>
      {error && (
        <p className="fn" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}
