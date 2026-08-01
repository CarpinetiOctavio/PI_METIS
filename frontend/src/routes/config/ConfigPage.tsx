import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import { postPreviewColumns } from "../../api/analysis";
import type { AnalysisStreamForm, ColumnaPreview, Modo, TipoVariable } from "../../api/types";
import "./ConfigPage.css";

// D3 (plan pasada4 §6) — preselección heurística, nunca obligatoria: el
// usuario siempre puede cambiar el <select> a mano. "Parece fecha/año" es
// deliberadamente laxo (4 dígitos, o cualquier cosa que Date.parse entienda)
// porque es solo una sugerencia de arranque, no una validación de contrato
// — esa la sigue haciendo el backend en el pipeline real.
function pareceFechaOAnio(muestra: string[]): boolean {
  if (muestra.length === 0) return false;
  return muestra.every((v) => /^\d{4}$/.test(v) || !Number.isNaN(Date.parse(v)));
}

function esNumerica(muestra: string[]): boolean {
  if (muestra.length === 0) return false;
  return muestra.every((v) => v.trim() !== "" && !Number.isNaN(Number(v)));
}

function preseleccionar(columnas: ColumnaPreview[]): { x: string; y: string } {
  const colX = columnas.find((c) => pareceFechaOAnio(c.muestra));
  const colY = columnas.find((c) => c !== colX && esNumerica(c.muestra));
  return {
    x: colX ? String(colX.indice) : "",
    y: colY ? String(colY.indice) : "",
  };
}

// Siempre se manda el índice como value (nunca el nombre) — _resolver_columna
// en el backend acepta un índice numérico igual que un nombre, y así un
// mismo esquema cubre nombres duplicados y archivos sin cabecera real sin
// necesitar dos caminos distintos (plan §6 D3, "caminos de error").
function etiquetaColumna(col: ColumnaPreview, todas: ColumnaPreview[]): string {
  const duplicado = todas.filter((c) => c.nombre === col.nombre).length > 1;
  const nombre = duplicado ? `${col.nombre} (col. ${col.indice + 1})` : col.nombre;
  const muestra = col.muestra.slice(0, 3).join(", ");
  return muestra ? `${nombre} — ${muestra}` : nombre;
}

type PreviewState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; columnas: ColumnaPreview[] }
  | { status: "error" };

export function ConfigPage() {
  const { isAuthed } = useAuth();
  const navigate = useNavigate();

  const [archivo, setArchivo] = useState<File | null>(null);
  const [preview, setPreview] = useState<PreviewState>({ status: "idle" });
  const [columnaX, setColumnaX] = useState("");
  const [columnaY, setColumnaY] = useState("");
  const [tipoVariable, setTipoVariable] = useState<TipoVariable>(
    "caudal_precipitacion",
  );
  const [modo, setModo] = useState<Modo>("paso_a_paso");
  const [error, setError] = useState<string | null>(null);

  // UX-D — el anónimo siempre usa la UI Experto, sin selector de modo
  // (frontend/frontend-design/metis-wireframes-fase1-decisiones.md, "UX-D").
  const modoEfectivo: Modo = isAuthed ? modo : "experto";

  async function handleFileChange(file: File | null) {
    setArchivo(file);
    // Las columnas de un archivo anterior no tienen por qué existir en el
    // nuevo — nunca dejar un índice/nombre stale seleccionado.
    setColumnaX("");
    setColumnaY("");

    if (!file) {
      setPreview({ status: "idle" });
      return;
    }

    setPreview({ status: "loading" });
    try {
      const response = await postPreviewColumns(file);
      if (!Array.isArray(response.columnas) || response.columnas.length === 0) {
        throw new Error("respuesta de preview-columns sin columnas utilizables");
      }
      setPreview({ status: "ready", columnas: response.columnas });
      const heuristica = preseleccionar(response.columnas);
      setColumnaX(heuristica.x);
      setColumnaY(heuristica.y);
    } catch {
      // "La previsualización falla → degradar a los inputs de texto
      // actuales con un aviso, nunca bloquear la ejecución del análisis."
      setPreview({ status: "error" });
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!archivo) {
      setError("Seleccioná un archivo CSV o Excel.");
      return;
    }
    if (!columnaX.trim() || !columnaY.trim()) {
      setError("Completá las dos columnas.");
      return;
    }
    setError(null);

    const form: AnalysisStreamForm = {
      archivo,
      columna_x: columnaX.trim(),
      columna_y: columnaY.trim(),
      tipo_variable: tipoVariable,
      modo: modoEfectivo,
      cramer_particion: "default",
    };
    // El form (incluido el File) viaja como router state — no persiste a un
    // refresh, pero StreamPage lo consume una sola vez al montar, así que no
    // hace falta un context aparte (ver frontend-implementation-plan.md §10, D9).
    navigate("/stream", { state: { form } });
  }

  return (
    <div className="card config-card">
      <h1 className="h">Nuevo análisis</h1>
      <p className="sub">Cargá tus datos, elegí el modo una vez y ejecutá.</p>
      {error && (
        <div className="banner crit" role="alert">
          <span className="ic">!</span> {error}
        </div>
      )}
      <form onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="config-archivo">Archivo (CSV o Excel)</label>
          <input
            id="config-archivo"
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={(event) => void handleFileChange(event.target.files?.[0] ?? null)}
          />
          {archivo && <p className="fn">{archivo.name}</p>}
        </div>
        <div className="row">
          <div className="col field">
            <label htmlFor="config-columna-x">Columna X</label>
            {preview.status === "ready" ? (
              <select
                id="config-columna-x"
                className="input"
                value={columnaX}
                onChange={(event) => setColumnaX(event.target.value)}
              >
                <option value="">Elegir columna…</option>
                {preview.columnas.map((col) => (
                  <option key={col.indice} value={col.indice}>
                    {etiquetaColumna(col, preview.columnas)}
                  </option>
                ))}
              </select>
            ) : (
              <input
                id="config-columna-x"
                className="input"
                type="text"
                value={columnaX}
                onChange={(event) => setColumnaX(event.target.value)}
              />
            )}
            {preview.status === "loading" && (
              <p className="fn">Buscando columnas…</p>
            )}
          </div>
          <div className="col field">
            <label htmlFor="config-columna-y">Columna Y</label>
            {preview.status === "ready" ? (
              <select
                id="config-columna-y"
                className="input"
                value={columnaY}
                onChange={(event) => setColumnaY(event.target.value)}
              >
                <option value="">Elegir columna…</option>
                {preview.columnas.map((col) => (
                  <option key={col.indice} value={col.indice}>
                    {etiquetaColumna(col, preview.columnas)}
                  </option>
                ))}
              </select>
            ) : (
              <input
                id="config-columna-y"
                className="input"
                type="text"
                value={columnaY}
                onChange={(event) => setColumnaY(event.target.value)}
              />
            )}
            {preview.status === "loading" && (
              <p className="fn">Buscando columnas…</p>
            )}
          </div>
        </div>
        {preview.status === "error" && (
          <div className="banner warn" style={{ marginBottom: 11 }}>
            <span className="ic">▲</span> No pudimos leer las columnas del
            archivo automáticamente. Completalas a mano — el análisis no se
            bloquea por esto.
          </div>
        )}
        <fieldset className="field">
          <legend>Tipo de variable</legend>
          <div className="seg">
            <button
              type="button"
              className={tipoVariable === "caudal_precipitacion" ? "on" : ""}
              aria-pressed={tipoVariable === "caudal_precipitacion"}
              onClick={() => setTipoVariable("caudal_precipitacion")}
            >
              Caudal/Precip.
            </button>
            <button
              type="button"
              className={tipoVariable === "otro" ? "on" : ""}
              aria-pressed={tipoVariable === "otro"}
              onClick={() => setTipoVariable("otro")}
            >
              Otro
            </button>
          </div>
        </fieldset>
        {isAuthed ? (
          <fieldset className="field">
            <legend>Modo · se elige una vez</legend>
            <div className="seg">
              <button
                type="button"
                className={modo === "paso_a_paso" ? "on" : ""}
                aria-pressed={modo === "paso_a_paso"}
                onClick={() => setModo("paso_a_paso")}
              >
                Paso a paso
              </button>
              <button
                type="button"
                className={modo === "experto" ? "on" : ""}
                aria-pressed={modo === "experto"}
                onClick={() => setModo("experto")}
              >
                Experto
              </button>
            </div>
            <p className="fn">
              Define la UI de todas las etapas. No se cambia después.
            </p>
          </fieldset>
        ) : (
          <div className="field">
            {/* S3 (limpieza SonarCloud): esto no es un <label> — no rotula
                ningún control, es una nota informativa de que el modo está
                fijo en anónimo. Sonar marcaba el <label> suelto anterior
                como huérfano (no apuntaba a nada vía htmlFor/aria-labelledby). */}
            <p className="ct">Modo</p>
            <div>
              <span className="tag">anónimo · solo resultados</span>
            </div>
          </div>
        )}
        <div className="card soft config-cramer">
          <p className="ct">Partición de Cramer</p>
          <div className="seg">
            <button type="button" className="on" disabled>
              Default 60/30
            </button>
            <button
              type="button"
              disabled
              title="No disponible — ver docs/decisiones/decision036.md"
            >
              Personalizada
            </button>
          </div>
          <p className="fn">La partición personalizada no está disponible todavía.</p>
        </div>
        <button
          type="submit"
          className="b b-pri"
          style={{ width: "100%", marginTop: 12 }}
        >
          Ejecutar análisis ▸
        </button>
      </form>
    </div>
  );
}
