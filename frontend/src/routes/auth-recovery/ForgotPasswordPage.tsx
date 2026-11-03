import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { forgotPassword } from "../../api/auth";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import { Magnet } from "../../components/Magnet";
import { SpecularHighlight } from "../../components/SpecularHighlight";

type Feedback = { kind: "ok" | "crit"; text: string };

// DECISIÓN 085: el backend responde igual exista o no la cuenta, así que la
// pantalla muestra siempre el mismo mensaje y no se puede usar para averiguar
// qué mails están registrados.
export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const enviado = feedback?.kind === "ok";

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setFeedback(null);
    setIsSubmitting(true);
    try {
      const response = await forgotPassword({ email });
      setFeedback({ kind: "ok", text: response.mensaje });
    } catch (err) {
      setFeedback({
        kind: "crit",
        text: err instanceof ApiError ? errorText(err.codigo) : errorText(""),
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="card"
      style={{ maxWidth: 420, margin: "40px auto" }}
    >
      <h1 className="h">Recuperar contraseña</h1>
      <p className="sub">
        Ingresá tu email institucional y te mandamos un link para elegir una
        contraseña nueva.
      </p>
      {feedback && (
        <div className={`banner ${feedback.kind}`} role="alert">
          <span className="ic">{enviado ? "✓" : "!"}</span> {feedback.text}
        </div>
      )}
      {!enviado && (
        <>
          <div className="field">
            <label htmlFor="forgot-email">Email institucional</label>
            <input
              id="forgot-email"
              className="input"
              type="email"
              placeholder="legajo@ucc.edu.ar"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>
          <Magnet>
            <SpecularHighlight>
              <button type="submit" className="b b-pri" disabled={isSubmitting}>
                {isSubmitting ? "Enviando…" : "Enviar link"}
              </button>
            </SpecularHighlight>
          </Magnet>
        </>
      )}
      <p className="entry__switch">
        <Link to="/" className="link-btn">
          Volver a la puerta de entrada
        </Link>
      </p>
    </form>
  );
}
