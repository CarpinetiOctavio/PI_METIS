import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import { postDesignEvents } from "../../api/etapa2";
import { PendingBadge } from "../../mocks/PendingBadge";
import type { DesignEventsResponse } from "../../api/types";
import "./DesignEventsPage.css";

const PERIODOS = [2, 5, 10, 25, 50, 100, 200, 500];

interface LocationState {
  distribucion?: string;
  metodo?: string;
}

type Axis = "calendario" | "hidrologico";

export function DesignEventsPage() {
  const location = useLocation();
  const { isAuthed } = useAuth();
  const state = location.state as LocationState | null;
  const distribucion = state?.distribucion ?? "Gumbel";
  const metodo = state?.metodo ?? "Momentos";

  const [data, setData] = useState<DesignEventsResponse | null>(null);
  const [selectedPeriodo, setSelectedPeriodo] = useState(100);
  const [axis, setAxis] = useState<Axis>("calendario");

  useEffect(() => {
    let cancelled = false;
    postDesignEvents({
      session_id: "mock-session",
      distribucion,
      metodo,
      periodos_retorno: PERIODOS,
    }).then((response) => {
      if (!cancelled) setData(response);
    });
    return () => {
      cancelled = true;
    };
  }, [distribucion, metodo]);

  if (!data) {
    return <p className="sub">Calculando eventos de diseño…</p>;
  }

  const selected = data.eventos_diseno.find(
    (e) => e.periodo_retorno === selectedPeriodo,
  );

  return (
    <div className="design-events-page">
      <div className="row" style={{ alignItems: "center" }}>
        <h1 className="h" style={{ marginBottom: 0 }}>
          Evento de diseño
        </h1>
        <span className="sp" />
        <PendingBadge note="/analysis/design-events no implementado — respuesta de ejemplo" />
      </div>
      <p className="sub">
        {data.distribucion} · {data.metodo}
      </p>

      <div className="card soft" style={{ textAlign: "center", padding: 22 }}>
        <div className="chips" style={{ justifyContent: "center", marginBottom: 14 }}>
          {PERIODOS.map((p) => (
            <button
              key={p}
              type="button"
              className={`chip${p === selectedPeriodo ? " on" : ""}`}
              aria-pressed={p === selectedPeriodo}
              onClick={() => setSelectedPeriodo(p)}
            >
              {p}
            </button>
          ))}
        </div>
        <div
          className="fn"
          style={{ textTransform: "uppercase", letterSpacing: 0.5, fontSize: 10 }}
        >
          Valor de diseño · T = {selectedPeriodo} años
        </div>
        <div className="num" style={{ fontSize: 38, fontWeight: 700 }}>
          {selected ? selected.valor : "—"}
        </div>
      </div>

      <div className="card" style={{ marginTop: 12 }}>
        <div className="row" style={{ alignItems: "center" }}>
          <p className="ct" style={{ margin: 0 }}>
            Curva de ajuste
          </p>
          <span className="sp" />
          <div className="seg" style={{ fontSize: 10 }}>
            <button
              type="button"
              className={axis === "calendario" ? "on" : ""}
              aria-pressed={axis === "calendario"}
              onClick={() => setAxis("calendario")}
            >
              Calendario
            </button>
            <button
              type="button"
              className={axis === "hidrologico" ? "on" : ""}
              aria-pressed={axis === "hidrologico"}
              onClick={() => setAxis("hidrologico")}
            >
              Hidrológico
            </button>
          </div>
        </div>
        <div className="chart" style={{ height: 130 }}>
          gráfico de ejemplo — {axis}
        </div>
      </div>

      {isAuthed && (
        <button
          type="button"
          className="b b-sec"
          disabled
          title="Exportación PDF pendiente — endpoint /export/{id} no implementado"
          style={{ marginTop: 12 }}
        >
          Exportar PDF (próximamente)
        </button>
      )}
    </div>
  );
}
