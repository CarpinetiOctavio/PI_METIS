import type { Etapa1Result, SimulateExclusionResponse, TestResultDetail } from "../../api/types";
import { errorText } from "../../i18n/errors.es";
import { formatInt, formatNum } from "../../i18n/format";
import { Etapa2RankingView } from "./Etapa2RankingView";
import { avisosNuevos, compararPruebas } from "./comparacionEtapa1";
import "./Etapa1Comparacion.css";

const NIVEL_INDEPENDENCIA: Record<NonNullable<Etapa1Result["nivel_independencia"]>, string> = {
  independiente: "independiente",
  dependiente: "dependiente",
};

const NIVEL_HOMOGENEIDAD: Record<NonNullable<Etapa1Result["nivel_homogeneidad"]>, string> = {
  homogeneidad_ok: "ok",
  homogeneidad_warning: "warning",
  homogeneidad_critica: "crítico",
};

const NIVEL_CONFIANZA: Record<Etapa1Result["nivel_confianza"], string> = {
  validado: "validado",
  con_warnings: "con warnings",
  rechazado: "rechazado",
};

function veredicto(t: TestResultDetail | null): string {
  if (!t) return "no se ejecutó";
  return (t.veredicto ?? "—").replace("_", " ");
}

function CeldaPrueba({ t }: Readonly<{ t: TestResultDetail | null }>) {
  return (
    <>
      {veredicto(t)}
      {t?.estadistico != null && <span className="fn"> ({formatNum(t.estadistico)})</span>}
    </>
  );
}

/**
 * Vista comparativa del what-if de atípicos (ítem A, A2 del plan de feedback de
 * directores): los veredictos originales contra los de la serie sin los puntos
 * excluidos, con el `n` de cada lado y lo que cambió resaltado. Solo presenta lo
 * que `core/` devolvió en cada corrida.
 *
 * `desactualizada` avisa que la selección de puntos cambió después de este
 * cálculo, así que lo que se ve ya no corresponde a lo que está marcado.
 */
export function Etapa1Comparacion({
  original,
  simulacion,
  desactualizada,
}: Readonly<{
  original: Etapa1Result;
  simulacion: SimulateExclusionResponse;
  desactualizada: boolean;
}>) {
  const { etapa1: simulado, excluidos } = simulacion;
  const bloqueado = simulado.contract.bloqueante;
  const filas = compararPruebas(original, simulado);
  const nuevos = avisosNuevos(original, simulado);
  const cambios = filas.filter((f) => f.cambio).length;

  const chow = simulado.atipicos.find((t) => t.prueba === "chow");
  const indiceAtipico = simulado.datos?.indice_atipico ?? null;
  const anioAtipico = indiceAtipico === null ? undefined : simulacion.anios[indiceAtipico];

  return (
    <div className="card etapa1-comparacion" aria-labelledby="etapa1-comparacion-titulo">
      <p className="ct" id="etapa1-comparacion-titulo">
        Resultados sin los puntos excluidos
      </p>

      {desactualizada && (
        <div className="banner warn" role="status">
          <span className="ic">▲</span> La selección cambió después de este cálculo: volvé a
          recalcular para ver los resultados de la selección actual.
        </div>
      )}

      <p className="fn">
        Se {excluidos.length === 1 ? "quitó" : "quitaron"}:{" "}
        {excluidos.map((e) => `${e.periodo} (${formatNum(e.valor_original)})`).join(", ")}.
        {original.descriptive && simulado.descriptive && (
          <>
            {" "}
            Datos: <b>{formatInt(original.descriptive.n)}</b> →{" "}
            <b>{formatInt(simulado.descriptive.n)}</b>.
          </>
        )}
      </p>

      {bloqueado ? (
        <div className="banner crit" role="alert">
          <span className="ic">✕</span>{" "}
          {simulado.contract.codigo_error
            ? errorText(simulado.contract.codigo_error)
            : "No se pudo analizar la serie sin esos puntos."}
        </div>
      ) : (
        <>
          <table className="t etapa1-comparacion__tabla">
            <thead>
              <tr>
                <th>Prueba</th>
                <th>Original</th>
                <th>Sin los puntos</th>
              </tr>
            </thead>
            <tbody>
              {filas.map((f) => (
                <tr key={f.prueba} data-cambio={f.cambio || undefined}>
                  <td>
                    {f.prueba} <span className="fn">· {f.grupo}</span>
                  </td>
                  <td>
                    <CeldaPrueba t={f.original} />
                  </td>
                  <td>
                    <CeldaPrueba t={f.simulado} />
                    {f.cambio && <span className="pill warn etapa1-comparacion__cambio">cambió</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="fn">
            {cambios === 0
              ? "Ningún veredicto cambia al quitar esos puntos."
              : `${formatInt(cambios)} ${cambios === 1 ? "veredicto cambia" : "veredictos cambian"} al quitar esos puntos.`}
          </p>

          <table className="t etapa1-comparacion__tabla">
            <thead>
              <tr>
                <th>Nivel</th>
                <th>Original</th>
                <th>Sin los puntos</th>
              </tr>
            </thead>
            <tbody>
              <FilaNivel
                etiqueta="Independencia"
                antes={original.nivel_independencia && NIVEL_INDEPENDENCIA[original.nivel_independencia]}
                despues={simulado.nivel_independencia && NIVEL_INDEPENDENCIA[simulado.nivel_independencia]}
              />
              <FilaNivel
                etiqueta="Homogeneidad"
                antes={original.nivel_homogeneidad && NIVEL_HOMOGENEIDAD[original.nivel_homogeneidad]}
                despues={simulado.nivel_homogeneidad && NIVEL_HOMOGENEIDAD[simulado.nivel_homogeneidad]}
              />
              <FilaNivel
                etiqueta="Resultado"
                antes={NIVEL_CONFIANZA[original.nivel_confianza]}
                despues={NIVEL_CONFIANZA[simulado.nivel_confianza]}
              />
            </tbody>
          </table>

          {chow?.veredicto === "rechazada" && (
            <p className="fn">
              Sin esos puntos, Chow marca otro dato como atípico
              {anioAtipico === undefined ? "" : ` (${anioAtipico})`}: {formatNum(chow.valor_atipico)}. Es
              solo una sugerencia; ahí no se frena nada.
            </p>
          )}

          {nuevos.length > 0 && (
            <div className="stack" style={{ marginTop: 10 }}>
              {nuevos.map((w) => (
                <div key={w.codigo} className={`banner ${w.nivel === "critico" ? "crit" : "warn"}`}>
                  <span className="ic">{w.nivel === "critico" ? "✕" : "▲"}</span> {w.descripcion}
                </div>
              ))}
            </div>
          )}

          {simulacion.etapa2 && (
            <div className="etapa1-comparacion__etapa2">
              <h3 className="h" style={{ fontSize: 15, marginBottom: 0 }}>
                Ranking de distribuciones sin esos puntos
              </h3>
              <Etapa2RankingView etapa2={simulacion.etapa2} modo="lectura" mediaSerie={simulado.descriptive?.media} />
            </div>
          )}
        </>
      )}
    </div>
  );
}

function FilaNivel({
  etiqueta,
  antes,
  despues,
}: Readonly<{ etiqueta: string; antes: string | null; despues: string | null }>) {
  const cambio = antes !== despues;
  return (
    <tr data-cambio={cambio || undefined}>
      <td>{etiqueta}</td>
      <td>{antes ?? "—"}</td>
      <td>
        {despues ?? "—"}
        {cambio && <span className="pill warn etapa1-comparacion__cambio">cambió</span>}
      </td>
    </tr>
  );
}
