import {
  useRef,
  useState,
  type CSSProperties,
  type DragEvent,
  type FormEvent,
  type KeyboardEvent,
  type PointerEvent,
} from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import { postPreviewColumns } from "../../api/analysis";
import type {
  AnalysisStreamForm,
  ColumnaPreview,
  CramerParticion,
  Modo,
  TipoVariable,
} from "../../api/types";
import { etiquetaSelectorMes } from "../../i18n/mesInicioAnio";
import { Magnet } from "../../components/Magnet";
import { SpecularHighlight } from "../../components/SpecularHighlight";
import { ColumnPreviewPanel } from "./ColumnPreviewPanel";
import { clamp, RESIZE_KEYBOARD_STEP, useColumnPanelDock } from "./useColumnPanelDock";
import "./ConfigPage.css";

const DOCE_MESES = Array.from({ length: 12 }, (_, i) => i + 1);

// Bloque E1 (pasada 5) — cap real de PARSE_FILE_TOO_LARGE (DECISIÓN 050), el
// frontend nunca lo mencionaba antes de la dropzone.
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// D3 (plan pasada4 §6) — preselección heurística, nunca obligatoria: el
// usuario siempre puede cambiar el <select> a mano. "Parece fecha/año" es
// deliberadamente laxo (4 dígitos, o cualquier cosa que Date.parse entienda)
// porque es solo una sugerencia de arranque, no una validación de contrato
// — esa la sigue haciendo el backend en el pipeline real.
function pareceFechaOAnio(muestra: string[]): boolean {
  if (muestra.length === 0) return false;
  return muestra.every((v) => /^\d{4}$/.test(v) || !Number.isNaN(Date.parse(v)));
}

// F5 (DECISIÓN 057) — a diferencia de pareceFechaOAnio() (deliberadamente
// laxa, para preseleccionar la columna X), acá hace falta distinguir año
// puro de fecha completa: el selector de mes de inicio no tiene sentido
// sobre una serie que ya es anual.
function esAnioPuro(muestra: string[]): boolean {
  if (muestra.length === 0) return false;
  return muestra.every((v) => /^\d{4}$/.test(v));
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
// Bloque E2 (pasada 5) — la etiqueta vuelve a ser solo el nombre. Ya no
// concatena la muestra (P8, se apelotonaba dentro del <option>) — la muestra
// completa ahora vive en ColumnPreviewPanel. La desambiguación de nombres
// duplicados se conserva: sin ella dos columnas homónimas son
// indistinguibles en el desplegable.
function etiquetaColumna(col: ColumnaPreview, todas: ColumnaPreview[]): string {
  const duplicado = todas.filter((c) => c.nombre === col.nombre).length > 1;
  return duplicado ? `${col.nombre} (col. ${col.indice + 1})` : col.nombre;
}

// Bloque H1 (plan post-avance, DECISIÓN 036) — mismas reglas que valida el
// backend (_parsear_cramer_particion, api/v1/analysis.py): 1-100, y
// n1_pct > n2_pct porque el bloque 1 es el período largo. Validado acá para
// mostrar el error inline antes de mandar el request, no como un 400
// CONTRACT_CRAMER_PARTICION_INVALID genérico — mismo patrón que
// parsePeriodosRetorno() en Etapa2RankingView.tsx.
function parseCramerParticion(
  modo: "default" | "personalizada",
  n1Input: string,
  n2Input: string,
): { value: CramerParticion } | { error: string } {
  if (modo === "default") return { value: "default" };

  const n1 = Number(n1Input);
  const n2 = Number(n2Input);
  if (!Number.isFinite(n1) || !Number.isFinite(n2)) {
    return { error: "Los dos porcentajes de la partición deben ser números." };
  }
  if (n1 < 1 || n1 > 100 || n2 < 1 || n2 > 100) {
    return { error: "Los dos porcentajes de la partición deben estar entre 1 y 100." };
  }
  if (n1 <= n2) {
    return {
      error:
        "El primer porcentaje (período largo) debe ser mayor que el segundo (período corto).",
    };
  }
  return { value: { n1_pct: n1, n2_pct: n2 } };
}

type PreviewState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; columnas: ColumnaPreview[]; filas: number }
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
  // Bloque H1 (plan post-avance, DECISIÓN 036) — inputs como texto libre
  // (no number controlado) para poder mostrar "" mientras el usuario borra
  // el campo, igual que el resto de los inputs de este formulario.
  const [cramerModo, setCramerModo] = useState<"default" | "personalizada">("default");
  const [cramerN1Input, setCramerN1Input] = useState("60");
  const [cramerN2Input, setCramerN2Input] = useState("30");
  // Bloque B6 del plan de Etapa 2 — sin selector antes, siempre se mandaba
  // "1" implícito (default de AnalysisStreamForm.etapas). DECISIÓN 054 solo
  // acepta "1" | "1,2" en el borde del endpoint.
  const [etapas, setEtapas] = useState<"1" | "1,2">("1");
  // Bloque F5 del plan de Etapa 2 (DECISIÓN 057) — default 7 (julio),
  // idéntico al default del backend. Se manda siempre, deshabilitado o no
  // (ver serieYaEsAnual más abajo) — el backend lo ignora cuando la
  // resolución ya es anual, así el frontend no necesita adivinar nada que
  // el backend no pueda re-verificar.
  const [mesInicioAnio, setMesInicioAnio] = useState(7);
  const [error, setError] = useState<string | null>(null);
  // Bloque E3 (pasada 5) — movida por onFocus/onBlur de los <select>, no por
  // su valor: resalta en ColumnPreviewPanel qué columna está eligiendo cada
  // uno ahora mismo.
  const [columnaResaltada, setColumnaResaltada] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  // Bloque E (plan post-avance) — posición de acople, ancho/alto y
  // abierto/cerrado del panel, persistidos en localStorage.
  const panel = useColumnPanelDock();
  const shellRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef<{ startPos: number; startSize: number; pendingSize: number } | null>(
    null,
  );

  // UX-D — el anónimo siempre usa la UI Experto, sin selector de modo
  // (frontend/frontend-design/metis-wireframes-fase1-decisiones.md, "UX-D").
  const modoEfectivo: Modo = isAuthed ? modo : "experto";

  // F5 — el selector de mes se deshabilita solo cuando la columna X elegida
  // es un año puro (serie ya anual, agregar no cambia nada). Sin preview
  // (inputs de texto de respaldo) no hay forma de saberlo: se deja
  // habilitado, mismo criterio conservador que el resto de esta pantalla
  // ante la ausencia de preview.
  const columnaXInfo =
    preview.status === "ready"
      ? preview.columnas.find((c) => String(c.indice) === columnaX)
      : undefined;
  const serieYaEsAnual = columnaXInfo ? esAnioPuro(columnaXInfo.muestra) : false;

  async function handleFileChange(file: File | null) {
    setArchivo(file);
    // Las columnas de un archivo anterior no tienen por qué existir en el
    // nuevo — nunca dejar un índice/nombre stale seleccionado.
    setColumnaX("");
    setColumnaY("");
    setColumnaResaltada(null);

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
      setPreview({ status: "ready", columnas: response.columnas, filas: response.filas });
      const heuristica = preseleccionar(response.columnas);
      setColumnaX(heuristica.x);
      setColumnaY(heuristica.y);
    } catch {
      // "La previsualización falla → degradar a los inputs de texto
      // actuales con un aviso, nunca bloquear la ejecución del análisis."
      setPreview({ status: "error" });
    }
  }

  // Bloque E1 — mismo camino de código que el onChange del input nativo. El
  // filtro por extensión del `accept` no se replica acá: si el usuario
  // suelta un archivo no soportado, se manda igual y el backend responde
  // PARSE_ERROR, que ya sabemos mostrar (preview.status === "error").
  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setDragOver(false);
    void handleFileChange(event.dataTransfer.files?.[0] ?? null);
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
    const cramerParticion = parseCramerParticion(cramerModo, cramerN1Input, cramerN2Input);
    if ("error" in cramerParticion) {
      setError(cramerParticion.error);
      return;
    }
    setError(null);

    const form: AnalysisStreamForm = {
      archivo,
      columna_x: columnaX.trim(),
      columna_y: columnaY.trim(),
      tipo_variable: tipoVariable,
      modo: modoEfectivo,
      cramer_particion: cramerParticion.value,
      etapas,
      mes_inicio_anio: mesInicioAnio,
    };
    // El form (incluido el File) viaja como router state — no persiste a un
    // refresh, pero StreamPage lo consume una sola vez al montar, así que no
    // hace falta un context aparte (ver frontend-implementation-plan.md §10, D9).
    navigate("/stream", { state: { form } });
  }

  // Bloque E (plan post-avance) — "right"/"bottom" anclan el panel al borde
  // opuesto al que se arrastra (el panel crece si el divisor se aleja de él);
  // "left" ancla al propio borde arrastrado (el panel crece si el divisor se
  // acerca al resto de la pantalla). Mismo signo para pointer y teclado.
  function cssVarNombre(dock: typeof panel.dock): string {
    return dock === "bottom" ? "--column-panel-height" : "--column-panel-width";
  }

  function handleResizePointerDown(event: PointerEvent<HTMLDivElement>) {
    // jsdom (tests) no implementa setPointerCapture — opcional a propósito,
    // el arrastre en sí no depende de la captura para funcionar acá.
    event.currentTarget.setPointerCapture?.(event.pointerId);
    const startPos = panel.dock === "bottom" ? event.clientY : event.clientX;
    dragRef.current = { startPos, startSize: panel.size, pendingSize: panel.size };
  }

  function handleResizePointerMove(event: PointerEvent<HTMLDivElement>) {
    if (!dragRef.current || !shellRef.current) return;
    const pos = panel.dock === "bottom" ? event.clientY : event.clientX;
    const delta =
      panel.dock === "left" ? pos - dragRef.current.startPos : dragRef.current.startPos - pos;
    const next = clamp(dragRef.current.startSize + delta, panel.limits.min, panel.limits.max);
    // Detalle de implementación (plan §E) — escribir directo a la custom
    // property vía ref, no vía setState: si no, cada píxel de arrastre
    // re-renderiza ConfigPage entera con sus dos <select> y el dropzone.
    // panel.setSize() recién se llama al soltar (pointerup/pointercancel).
    shellRef.current.style.setProperty(cssVarNombre(panel.dock), `${next}px`);
    dragRef.current.pendingSize = next;
  }

  function handleResizePointerUp() {
    if (dragRef.current) panel.setSize(dragRef.current.pendingSize);
    dragRef.current = null;
  }

  function handleResizeKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const esVertical = panel.dock !== "bottom";
    let delta = 0;
    if (esVertical) {
      if (event.key === "ArrowLeft") delta = panel.dock === "right" ? RESIZE_KEYBOARD_STEP : -RESIZE_KEYBOARD_STEP;
      else if (event.key === "ArrowRight") delta = panel.dock === "right" ? -RESIZE_KEYBOARD_STEP : RESIZE_KEYBOARD_STEP;
    } else {
      if (event.key === "ArrowUp") delta = RESIZE_KEYBOARD_STEP;
      else if (event.key === "ArrowDown") delta = -RESIZE_KEYBOARD_STEP;
    }
    if (delta === 0) return;
    event.preventDefault();
    panel.setSize(clamp(panel.size + delta, panel.limits.min, panel.limits.max));
  }

  const panelVisible = preview.status === "ready" && panel.open;
  const shellStyle: CSSProperties | undefined = panelVisible
    ? ({ [cssVarNombre(panel.dock)]: `${panel.size}px` } as CSSProperties)
    : undefined;

  return (
    <div
      ref={shellRef}
      data-dock={panel.dock}
      className={`config-shell${panelVisible ? " config-shell--with-panel" : ""}`}
      style={shellStyle}
    >
      <div className="card config-card">
        <h1 className="h">Nuevo análisis</h1>
        <p className="sub">Cargá tus datos, elegí el modo una vez y ejecutá.</p>
        {preview.status === "ready" && !panel.open && (
          <button
            type="button"
            className="b b-sec"
            style={{ marginBottom: 11 }}
            onClick={() => panel.setOpen(true)}
          >
            Ver columnas
          </button>
        )}
        {error && (
          <div className="banner crit" role="alert">
            <span className="ic">!</span> {error}
          </div>
        )}
        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            {/* Bloque E1 (pasada 5) — el <input> nativo no desaparece, sigue
                siendo el único destino real de la selección/drop (mismo
                handleFileChange para los dos gestos). Se oculta visualmente
                y su <label> pasa a ser toda la zona de arrastre. El nombre
                accesible "Archivo (CSV o Excel)" va en un aria-label sobre
                el propio <input> — no en el texto del <label> — porque el
                <label> ahora envuelve el contenido visual del dropzone
                (icono, mensaje, nombre de archivo) y ese texto no puede
                ser también el nombre accesible del control sin duplicarlo
                cada vez que cambia. aria-label en el elemento etiquetado
                tiene precedencia sobre cualquier <label> asociado — el
                contenido visual queda aria-hidden por claridad, aunque ya
                no participa del cómputo del nombre accesible de todos
                modos. */}
            <label
              htmlFor="config-archivo"
              data-testid="config-dropzone"
              className={`config-dropzone${dragOver ? " config-dropzone--drag" : ""}`}
              onDragOver={(event) => {
                event.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
            >
              <div className="config-dropzone__content" aria-hidden="true">
                {archivo ? (
                  <>
                    <span className="config-dropzone__name">{archivo.name}</span>
                    <span className="fn">{formatFileSize(archivo.size)}</span>
                    <span className="config-dropzone__change">Cambiar</span>
                  </>
                ) : (
                  <>
                    <span className="config-dropzone__icon">⬆</span>
                    <p>Buscá un archivo o arrastralo acá</p>
                    <p className="fn">CSV, XLSX o XLS · hasta 10 MB</p>
                  </>
                )}
              </div>
            </label>
            <input
              id="config-archivo"
              type="file"
              accept=".csv,.xlsx,.xls"
              aria-label="Archivo (CSV o Excel)"
              className="visually-hidden"
              onChange={(event) => void handleFileChange(event.target.files?.[0] ?? null)}
            />
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
                  onFocus={() => setColumnaResaltada(columnaX || null)}
                  onBlur={() => setColumnaResaltada(null)}
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
                  onFocus={() => setColumnaResaltada(columnaY || null)}
                  onBlur={() => setColumnaResaltada(null)}
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
          <div className="field">
            <label htmlFor="config-mes-inicio">Mes de inicio del año</label>
            <select
              id="config-mes-inicio"
              className="input"
              value={mesInicioAnio}
              disabled={serieYaEsAnual}
              onChange={(event) => setMesInicioAnio(Number(event.target.value))}
            >
              {DOCE_MESES.map((mes) => (
                <option key={mes} value={mes}>
                  {etiquetaSelectorMes(mes)}
                </option>
              ))}
            </select>
            <p className="fn">
              {serieYaEsAnual
                ? "La columna X ya son años — este criterio no aplica, la serie no se agrega."
                : "Define cómo se agrupan los datos en años antes de analizar la serie (solo tiene efecto si la serie es mensual)."}
            </p>
          </div>
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
          <fieldset className="field">
            <legend>Alcance del análisis</legend>
            <div className="seg">
              <button
                type="button"
                className={etapas === "1" ? "on" : ""}
                aria-pressed={etapas === "1"}
                onClick={() => setEtapas("1")}
              >
                Solo validación (Etapa 1)
              </button>
              <button
                type="button"
                className={etapas === "1,2" ? "on" : ""}
                aria-pressed={etapas === "1,2"}
                onClick={() => setEtapas("1,2")}
              >
                Validación + análisis de frecuencia (Etapa 1 y 2)
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
          {/* Bloque H1 (plan post-avance, DECISIÓN 036) — antes deshabilitado
              por completo (el backend no podía recibir una partición
              personalizada sin crashear, ver decision036.md). */}
          <div className="card soft config-cramer">
            <p className="ct">Partición de Cramer</p>
            <div className="seg">
              <button
                type="button"
                className={cramerModo === "default" ? "on" : ""}
                aria-pressed={cramerModo === "default"}
                onClick={() => setCramerModo("default")}
              >
                Default 60/30
              </button>
              <button
                type="button"
                className={cramerModo === "personalizada" ? "on" : ""}
                aria-pressed={cramerModo === "personalizada"}
                onClick={() => setCramerModo("personalizada")}
              >
                Personalizada
              </button>
            </div>
            {cramerModo === "personalizada" && (
              <div className="row" style={{ marginTop: 8 }}>
                <div className="col field">
                  <label htmlFor="config-cramer-n1">% período largo</label>
                  <input
                    id="config-cramer-n1"
                    className="input"
                    type="text"
                    inputMode="decimal"
                    value={cramerN1Input}
                    onChange={(event) => setCramerN1Input(event.target.value)}
                  />
                </div>
                <div className="col field">
                  <label htmlFor="config-cramer-n2">% período corto</label>
                  <input
                    id="config-cramer-n2"
                    className="input"
                    type="text"
                    inputMode="decimal"
                    value={cramerN2Input}
                    onChange={(event) => setCramerN2Input(event.target.value)}
                  />
                </div>
              </div>
            )}
            {/* Nota de dominio (formulas-etapa1.md §6) — sin esto, dos
                porcentajes sugieren razonablemente "principio y final" del
                registro, cuando en realidad los dos se toman siempre del
                final. */}
            <p className="fn">
              {cramerModo === "default"
                ? "Los dos bloques (60% y 30%) se toman del final del registro."
                : "Los dos bloques se toman del final del registro — el primer porcentaje es el período más largo."}
            </p>
          </div>
          <Magnet style={{ width: "100%", marginTop: 12 }}>
            <SpecularHighlight style={{ width: "100%" }}>
              <button type="submit" className="b b-pri" style={{ width: "100%" }}>
                Ejecutar análisis ▸
              </button>
            </SpecularHighlight>
          </Magnet>
        </form>
      </div>
      {panelVisible && (
        <>
          <div
            className="config-shell__divider"
            role="separator"
            aria-orientation={panel.dock === "bottom" ? "horizontal" : "vertical"}
            aria-label="Redimensionar panel de columnas"
            aria-valuenow={Math.round(panel.size)}
            aria-valuemin={panel.limits.min}
            aria-valuemax={panel.limits.max}
            tabIndex={0}
            onPointerDown={handleResizePointerDown}
            onPointerMove={handleResizePointerMove}
            onPointerUp={handleResizePointerUp}
            onPointerCancel={handleResizePointerUp}
            onKeyDown={handleResizeKeyDown}
          />
          <ColumnPreviewPanel
            columnas={preview.columnas}
            filas={preview.filas}
            columnaResaltada={columnaResaltada}
            dock={panel.dock}
            onDockChange={panel.setDock}
            onClose={() => panel.setOpen(false)}
          />
        </>
      )}
    </div>
  );
}
