import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { archiveAnalysis, listHistory, unarchiveAnalysis } from "../../api/history";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import type { HistoryItem } from "../../api/types";
import { SpotlightCard } from "../../components/SpotlightCard";
import "./HistoryPage.css";

const PAGE_SIZE = 10;
const UNDO_TIMEOUT_MS = 6000;

export function HistoryPage() {
  const [viewArchived, setViewArchived] = useState(false);
  const [items, setItems] = useState<HistoryItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [undo, setUndo] = useState<{ item: HistoryItem; timer: number } | null>(null);

  useEffect(() => {
    let cancelled = false;
    setItems(null);
    setPage(0);
    listHistory(viewArchived)
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof ApiError ? errorText(err.codigo) : errorText(""));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [viewArchived]);

  useEffect(() => {
    // El timer de deshacer vive fuera del render — se limpia al desmontar
    // la página o al reemplazarlo por uno nuevo, para no dejar un
    // setTimeout huérfano que intente actualizar un componente ya fuera.
    return () => {
      if (undo) window.clearTimeout(undo.timer);
    };
  }, [undo]);

  function handleArchived(item: HistoryItem) {
    setItems((prev) => (prev ? prev.filter((i) => i.id !== item.id) : prev));
    if (undo) window.clearTimeout(undo.timer);
    const timer = window.setTimeout(() => setUndo(null), UNDO_TIMEOUT_MS);
    setUndo({ item, timer });
  }

  function handleUnarchived(item: HistoryItem) {
    setItems((prev) => (prev ? prev.filter((i) => i.id !== item.id) : prev));
  }

  async function handleUndo() {
    if (!undo) return;
    window.clearTimeout(undo.timer);
    const { item } = undo;
    setUndo(null);
    try {
      await unarchiveAnalysis(item.id);
      if (!viewArchived) {
        setItems((prev) => (prev ? [item, ...prev] : [item]));
      }
    } catch {
      // Si el deshacer falla, el análisis sigue archivado — no hay nada más
      // que hacer acá, el usuario puede desarchivarlo desde "Ver archivados".
    }
  }

  if (error) {
    return (
      <div className="banner crit" role="alert">
        <span className="ic">!</span> {error}
      </div>
    );
  }

  return (
    <div className="history-page">
      <div className="row history-header">
        <h1 className="h">Tu historial</h1>
        <span className="sp" />
        <button
          type="button"
          className="b b-sec"
          onClick={() => setViewArchived((v) => !v)}
        >
          {viewArchived ? "Ver activos" : "Ver archivados"}
        </button>
      </div>

      {!items ? (
        <p className="sub">Cargando historial…</p>
      ) : items.length === 0 ? (
        <div className="card">
          <p className="sub">
            {viewArchived
              ? "No tenés análisis archivados."
              : "Todavía no tenés análisis guardados."}
          </p>
        </div>
      ) : (
        <HistoryList
          items={items}
          page={page}
          onPageChange={setPage}
          viewArchived={viewArchived}
          onArchived={handleArchived}
          onUnarchived={handleUnarchived}
        />
      )}

      {undo && (
        <div className="history-undo-toast" role="status">
          <span>Análisis archivado.</span>
          <button type="button" className="link-btn" onClick={handleUndo}>
            Deshacer
          </button>
        </div>
      )}
    </div>
  );
}

function HistoryList({
  items,
  page,
  onPageChange,
  viewArchived,
  onArchived,
  onUnarchived,
}: Readonly<{
  items: HistoryItem[];
  page: number;
  onPageChange: (page: number) => void;
  viewArchived: boolean;
  onArchived: (item: HistoryItem) => void;
  onUnarchived: (item: HistoryItem) => void;
}>) {
  // El backend devuelve un array plano sin paginación (ver
  // frontend-integration.md §3, discrepancia de forma en GET /history/) —
  // paginamos acá para no renderizar listas enormes de una sola vez.
  const totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
  const pageItems = items.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

  return (
    <>
      <div className="stack">
        {pageItems.map((item) => (
          <HistoryRow
            key={item.id}
            item={item}
            viewArchived={viewArchived}
            onArchived={onArchived}
            onUnarchived={onUnarchived}
          />
        ))}
      </div>
      {totalPages > 1 && (
        <div className="row history-pagination">
          <button
            type="button"
            className="b b-sec"
            disabled={page === 0}
            onClick={() => onPageChange(page - 1)}
          >
            ◂ Anterior
          </button>
          <span className="fn">
            Página {page + 1} de {totalPages}
          </span>
          <button
            type="button"
            className="b b-sec"
            disabled={page >= totalPages - 1}
            onClick={() => onPageChange(page + 1)}
          >
            Siguiente ▸
          </button>
        </div>
      )}
    </>
  );
}

function HistoryRow({
  item,
  viewArchived,
  onArchived,
  onUnarchived,
}: Readonly<{
  item: HistoryItem;
  viewArchived: boolean;
  onArchived: (item: HistoryItem) => void;
  onUnarchived: (item: HistoryItem) => void;
}>) {
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);

  async function confirmArchive() {
    setBusy(true);
    try {
      await archiveAnalysis(item.id);
      onArchived(item);
    } finally {
      setBusy(false);
      setConfirming(false);
    }
  }

  async function handleUnarchive() {
    setBusy(true);
    try {
      await unarchiveAnalysis(item.id);
      onUnarchived(item);
    } finally {
      setBusy(false);
    }
  }

  return (
    // Nota HTML: los botones de acción viven fuera del <Link> a propósito —
    // un <a> no puede contener elementos interactivos anidados (<button>)
    // sin producir HTML inválido / comportamiento de foco inconsistente
    // entre navegadores. El <Link> cubre solo el contenido no interactivo;
    // los botones son hermanos, no hijos.
    <SpotlightCard className="history-item">
      <Link to={`/history/${item.id}`} className="history-item-link">
        <div className="row" style={{ alignItems: "center" }}>
          <b>{item.tipo_variable}</b>
          <span className="sp" />
          <span className="fn">{new Date(item.created_at).toLocaleString("es-AR")}</span>
        </div>
        <p className="fn">
          Modo: {item.modo ?? "—"} · Etapas: {item.etapas?.join(", ") ?? "—"}
        </p>
      </Link>
      <div className="row history-item-actions">
        {viewArchived ? (
          <button
            type="button"
            className="b b-sec"
            disabled={busy}
            onClick={handleUnarchive}
          >
            Desarchivar
          </button>
        ) : confirming ? (
          <>
            <span className="fn">¿Archivar este análisis?</span>
            <button
              type="button"
              className="b b-sec"
              disabled={busy}
              onClick={confirmArchive}
            >
              Sí, archivar
            </button>
            <button
              type="button"
              className="link-btn"
              onClick={() => setConfirming(false)}
            >
              Cancelar
            </button>
          </>
        ) : (
          <button type="button" className="link-btn" onClick={() => setConfirming(true)}>
            Archivar
          </button>
        )}
      </div>
    </SpotlightCard>
  );
}
