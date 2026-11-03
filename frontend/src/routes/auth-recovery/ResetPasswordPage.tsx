import { useState, type FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { resetPassword } from "../../api/auth";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import { Magnet } from "../../components/Magnet";
import { SpecularHighlight } from "../../components/SpecularHighlight";

const LARGO_MINIMO = 8; // mismo criterio que register (backend: _validar_largo_password)

type Feedback = { kind: "ok" | "crit"; text: string };

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [password, setPassword] = useState("");
  const [confirmacion, setConfirmacion] = useState("");
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const listo = feedback?.kind === "ok";

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    if (password.length < LARGO_MINIMO) {
      setFeedback({
        kind: "crit",
        text: `La contraseña debe tener al menos ${LARGO_MINIMO} caracteres.`,
      });
      return;
    }
    if (password !== confirmacion) {
      setFeedback({ kind: "crit", text: "Las contraseñas no coinciden." });
      return;
    }
    setFeedback(null);
    setIsSubmitting(true);
    try {
      await resetPassword({ token, password });
      setFeedback({
        kind: "ok",
        text: "Contraseña actualizada. Ya podés iniciar sesión con la nueva.",
      });
    } catch (err) {
      setFeedback({
        kind: "crit",
        text: err instanceof ApiError ? errorText(err.codigo) : errorText(""),
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!token) {
    return (
      <div className="card" style={{ maxWidth: 420, margin: "40px auto" }}>
        <h1 className="h">Restablecer contraseña</h1>
        <div className="banner crit" role="alert">
          <span className="ic">!</span> Falta el token en el link. Pedí uno nuevo
          para continuar.
        </div>
        <p className="entry__switch">
          <Link to="/auth/forgot-password" className="link-btn">
            Pedir un link nuevo
          </Link>
        </p>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="card"
      style={{ maxWidth: 420, margin: "40px auto" }}
    >
      <h1 className="h">Restablecer contraseña</h1>
      {feedback && (
        <div className={`banner ${feedback.kind}`} role="alert">
          <span className="ic">{listo ? "✓" : "!"}</span> {feedback.text}
        </div>
      )}
      {!listo && (
        <>
          <div className="field">
            <label htmlFor="reset-password">Contraseña nueva</label>
            <input
              id="reset-password"
              className="input"
              type="password"
              autoComplete="new-password"
              minLength={LARGO_MINIMO}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="reset-confirmacion">Repetí la contraseña</label>
            <input
              id="reset-confirmacion"
              className="input"
              type="password"
              autoComplete="new-password"
              value={confirmacion}
              onChange={(event) => setConfirmacion(event.target.value)}
              required
            />
          </div>
          <Magnet>
            <SpecularHighlight>
              <button type="submit" className="b b-pri" disabled={isSubmitting}>
                {isSubmitting ? "Guardando…" : "Guardar contraseña"}
              </button>
            </SpecularHighlight>
          </Magnet>
        </>
      )}
      <p className="entry__switch">
        {listo ? (
          <Link to="/" className="link-btn">
            Ir a la puerta de entrada
          </Link>
        ) : (
          <Link to="/auth/forgot-password" className="link-btn">
            Pedir un link nuevo
          </Link>
        )}
      </p>
    </form>
  );
}
