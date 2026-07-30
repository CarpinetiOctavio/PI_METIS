import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { verify } from "../../api/auth";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";

type Status = "checking" | "success" | "error";

// R4 (limpieza SonarCloud): reemplaza los dos ternarios anidados
// (bannerKind e ícono) — mismo patrón Record<Status, X> que ya usa el
// resto del proyecto (STEP_CLASS, PILL_LABEL, NIVEL_CONFIANZA_KIND).
const BANNER_KIND: Record<Status, string> = {
  success: "ok",
  error: "crit",
  checking: "info",
};

const STATUS_ICON: Record<Status, string> = {
  success: "✓",
  error: "!",
  checking: "…",
};

export function AuthVerifyPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<Status>("checking");
  const [message, setMessage] = useState("Verificando cuenta…");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Falta el token de verificación en el link.");
      return;
    }

    let cancelled = false;
    verify({ token })
      .then(() => {
        if (cancelled) return;
        setStatus("success");
        setMessage("Cuenta verificada. Ya podés iniciar sesión.");
      })
      .catch((err) => {
        if (cancelled) return;
        setStatus("error");
        setMessage(err instanceof ApiError ? errorText(err.codigo) : errorText(""));
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="card" style={{ maxWidth: 420, margin: "40px auto" }}>
      <h1 className="h">Verificación de cuenta</h1>
      {/* N2 (limpieza SonarCloud): <output> ya tiene role="status" implícito
          — el atributo explícito era ARIA redundante sobre un elemento
          nativo que ya lo expresa. */}
      <output className={`banner ${BANNER_KIND[status]}`}>
        <span className="ic">{STATUS_ICON[status]}</span> {message}
      </output>
      {status !== "checking" && (
        <Link to="/" className="b b-pri" style={{ marginTop: 12 }}>
          Ir a la puerta de entrada
        </Link>
      )}
    </div>
  );
}
