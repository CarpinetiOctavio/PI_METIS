import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { verify } from "../../api/auth";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";

type Status = "checking" | "success" | "error";

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

  const bannerKind = status === "success" ? "ok" : status === "error" ? "crit" : "info";

  return (
    <div className="card" style={{ maxWidth: 420, margin: "40px auto" }}>
      <h1 className="h">Verificación de cuenta</h1>
      <div className={`banner ${bannerKind}`} role="status">
        <span className="ic">
          {status === "success" ? "✓" : status === "error" ? "!" : "…"}
        </span>{" "}
        {message}
      </div>
      {status !== "checking" && (
        <Link to="/" className="b b-pri" style={{ marginTop: 12 }}>
          Ir a la puerta de entrada
        </Link>
      )}
    </div>
  );
}
