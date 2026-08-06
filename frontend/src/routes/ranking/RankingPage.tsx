import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { rankingMock } from "../../mocks/etapa2.mock";
import { PendingBadge } from "../../mocks/PendingBadge";
import { formatNum } from "../../i18n/format";
import type { RankingItem } from "../../api/types";
import { Magnet } from "../../components/Magnet";
import { SpecularHighlight } from "../../components/SpecularHighlight";
import "./RankingPage.css";

type Axis = "calendario" | "hidrologico";

// D5 (pasada de mejora): antes `axis` vivía en RankingPage, una sola vez
// para toda la grilla — el toggle calendario/hidrológico se renderizaba
// POR tarjeta pero las 8 leían y escribían el mismo estado, así que tocar
// el toggle en una tarjeta cambiaba las ocho. Extraído a un componente por
// tarjeta con su propio estado local.
function RankingCard({
  item,
  onElegir,
}: Readonly<{
  item: RankingItem;
  onElegir: () => void;
}>) {
  const [axis, setAxis] = useState<Axis>("calendario");

  return (
    <div className={`card ranking-card${item.rank === 1 ? " top" : ""}`}>
      <div className="row">
        <span className={`pill ${item.rank === 1 ? "ok" : "wait"}`}>
          #{item.rank}
        </span>
        {item.rank === 1 && <span className="pill ok">menor EEA</span>}
      </div>
      <h3 className="h" style={{ fontSize: 15, marginTop: 9 }}>
        {item.distribucion}
      </h3>
      <p className="sub" style={{ margin: "2px 0 8px" }}>
        {item.metodo}
      </p>
      <div className="seg" style={{ fontSize: 10, marginBottom: 8 }}>
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
      <div className="chart" style={{ height: 70 }}>
        gráfico de ejemplo — {axis}
      </div>
      <p className="fn">
        EEA <span className="num">{formatNum(item.eea)}</span>
      </p>
      {item.rank === 1 ? (
        // Magnet + Specular Highlight — solo botones primarios (05/08/2026,
        // veredicto final). El de mayor rank siempre es b-sec, sin envolver.
        <Magnet style={{ width: "100%", marginTop: 9 }}>
          <SpecularHighlight style={{ width: "100%" }}>
            <button type="button" className="b b-pri" style={{ width: "100%" }} onClick={onElegir}>
              Elegir
            </button>
          </SpecularHighlight>
        </Magnet>
      ) : (
        <button
          type="button"
          className="b b-sec"
          style={{ width: "100%", marginTop: 9 }}
          onClick={onElegir}
        >
          Elegir
        </button>
      )}
    </div>
  );
}

export function RankingPage() {
  const navigate = useNavigate();

  return (
    <div className="ranking-page">
      <div className="row" style={{ alignItems: "center" }}>
        <h1 className="h" style={{ marginBottom: 0 }}>
          Mejores ajustes
        </h1>
        <span className="sp" />
        <PendingBadge note="Etapa 2 no expuesta por API todavía — ranking de ejemplo" />
      </div>
      <p className="sub">
        METIS ordena por EEA; la distribución la elegís vos.
      </p>

      <div className="ranking-grid">
        {rankingMock.map((item) => (
          <RankingCard
            key={`${item.distribucion}-${item.metodo}`}
            item={item}
            onElegir={() =>
              navigate("/design-events", {
                state: { distribucion: item.distribucion, metodo: item.metodo },
              })
            }
          />
        ))}
      </div>
    </div>
  );
}
