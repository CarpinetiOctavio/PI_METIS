import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import type { AnalysisStreamForm, Modo, TipoVariable } from "../../api/types";
import "./ConfigPage.css";

export function ConfigPage() {
  const { isAuthed } = useAuth();
  const navigate = useNavigate();

  const [archivo, setArchivo] = useState<File | null>(null);
  const [columnaX, setColumnaX] = useState("");
  const [columnaY, setColumnaY] = useState("");
  const [tipoVariable, setTipoVariable] = useState<TipoVariable>(
    "caudal_precipitacion",
  );
  const [modo, setModo] = useState<Modo>("paso_a_paso");
  const [error, setError] = useState<string | null>(null);

  // Decisión D — el anónimo siempre usa la UI Experto, sin selector de modo
  // (metis-wireframes-fase1-decisiones.md, "Decisión de arquitectura D").
  const modoEfectivo: Modo = isAuthed ? modo : "experto";

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
            onChange={(event) => setArchivo(event.target.files?.[0] ?? null)}
          />
          {archivo && <p className="fn">{archivo.name}</p>}
        </div>
        <div className="row">
          <div className="col field">
            <label htmlFor="config-columna-x">Columna X</label>
            <input
              id="config-columna-x"
              className="input"
              type="text"
              value={columnaX}
              onChange={(event) => setColumnaX(event.target.value)}
            />
          </div>
          <div className="col field">
            <label htmlFor="config-columna-y">Columna Y</label>
            <input
              id="config-columna-y"
              className="input"
              type="text"
              value={columnaY}
              onChange={(event) => setColumnaY(event.target.value)}
            />
          </div>
        </div>
        <div className="field">
          <label id="tipo-variable-label">Tipo de variable</label>
          <div className="seg" role="group" aria-labelledby="tipo-variable-label">
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
        </div>
        {isAuthed ? (
          <div className="field">
            <label id="modo-label">Modo · se elige una vez</label>
            <div className="seg" role="group" aria-labelledby="modo-label">
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
          </div>
        ) : (
          <div className="field">
            <label>Modo</label>
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
              title="No disponible — partición personalizada rota en el backend actual"
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
