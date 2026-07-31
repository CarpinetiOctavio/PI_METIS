import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import { Etapa1ResultView } from "./Etapa1ResultView";
import { PendingBadge } from "../../mocks/PendingBadge";
import type { Etapa1Result, Modo } from "../../api/types";
import "./ResultsPage.css";

interface ResultsLocationState {
  result?: Etapa1Result;
  analysisId?: string | null;
  modo?: Modo;
}

export function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthed } = useAuth();

  const locationState = location.state as ResultsLocationState | null;
  const result = locationState?.result;

  useEffect(() => {
    if (!result) navigate("/config", { replace: true });
  }, [result, navigate]);

  if (!result) return null;

  // UX-D — anónimo siempre ve la presentación Experto, sin acordeón.
  const modoEfectivo: Modo = isAuthed ? (locationState?.modo ?? "experto") : "experto";

  return (
    <div className="results-page">
      <h1 className="h">Resultados de Etapa 1</h1>
      <Etapa1ResultView result={result} modo={modoEfectivo} />
      {/* F5 (informe-diagnostico-ui-rota.md): antes ninguna pantalla
          navegaba a /ranking — Etapa 2 era inalcanzable salvo tipeando la
          URL. Se muestra igual con el PendingBadge (no se oculta hasta que
          el backend exponga Etapa 2 de verdad, DECISIÓN 042) porque el
          tribunal necesita ver el flujo completo de CU-01; el badge deja
          explícito qué parte es mock. */}
      <div className="row" style={{ marginTop: 20, alignItems: "center", gap: 10 }}>
        <button
          type="button"
          className="b b-pri"
          onClick={() => navigate("/ranking")}
        >
          Continuar a Etapa 2 ▸
        </button>
        <PendingBadge note="Etapa 2 no expuesta por API todavía — ranking de ejemplo" />
      </div>
    </div>
  );
}
