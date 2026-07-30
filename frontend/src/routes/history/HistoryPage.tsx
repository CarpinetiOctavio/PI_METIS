import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listHistory } from "../../api/history";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import type { HistoryItem } from "../../api/types";
import "./HistoryPage.css";

const PAGE_SIZE = 10;

export function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);

  useEffect(() => {
    let cancelled = false;
    listHistory()
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
  }, []);

  if (error) {
    return (
      <div className="banner crit" role="alert">
        <span className="ic">!</span> {error}
      </div>
    );
  }

  if (!items) {
    return <p className="sub">Cargando historial…</p>;
  }

  return (
    <div className="history-page">
      <h1 className="h">Tu historial</h1>
      {items.length === 0 ? (
        <div className="card">
          <p className="sub">Todavía no tenés análisis guardados.</p>
        </div>
      ) : (
        <HistoryList items={items} page={page} onPageChange={setPage} />
      )}
    </div>
  );
}

function HistoryList({
  items,
  page,
  onPageChange,
}: Readonly<{
  items: HistoryItem[];
  page: number;
  onPageChange: (page: number) => void;
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
          <Link key={item.id} to={`/history/${item.id}`} className="card history-item">
            <div className="row" style={{ alignItems: "center" }}>
              <b>{item.tipo_variable}</b>
              <span className="sp" />
              <span className="fn">
                {new Date(item.created_at).toLocaleString("es-AR")}
              </span>
            </div>
            <p className="fn">
              Modo: {item.modo ?? "—"} · Etapas: {item.etapas?.join(", ") ?? "—"}
            </p>
          </Link>
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
