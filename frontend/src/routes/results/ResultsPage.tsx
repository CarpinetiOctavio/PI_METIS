import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import { Etapa1ResultView } from "./Etapa1ResultView";
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

  // Decisión D — anónimo siempre ve la presentación Experto, sin acordeón.
  const modoEfectivo: Modo = isAuthed ? (locationState?.modo ?? "experto") : "experto";

  return (
    <div className="results-page">
      <h1 className="h">Resultados de Etapa 1</h1>
      <Etapa1ResultView result={result} modo={modoEfectivo} />
    </div>
  );
}
