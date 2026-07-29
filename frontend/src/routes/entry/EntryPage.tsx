import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import { register as registerRequest } from "../../api/auth";
import { ApiError } from "../../api/client";
import { errorText } from "../../i18n/errors.es";
import "./EntryPage.css";

type Mode = "login" | "register";

export function EntryPage() {
  const [mode, setMode] = useState<Mode>("login");

  return (
    <>
      {/* Encabezado accesible único de la pantalla — el título visible de cada
          formulario (h3 "Iniciar sesión" / "Crear cuenta") vive más abajo,
          fiel a la variante A del prototipo. */}
      <h1 className="visually-hidden">Puerta de entrada</h1>
      <div className="entry">
        <div className="entry__brand">
          <span className="logo">METIS</span>
          <p className="sub" style={{ marginTop: 12 }}>
            Análisis de frecuencia de eventos extremos hidrológicos. Acceso
            institucional UCC.
          </p>
        </div>
        <div className="entry__form">
          {mode === "login" ? (
            <LoginForm onSwitchToRegister={() => setMode("register")} />
          ) : (
            <RegisterForm onSwitchToLogin={() => setMode("login")} />
          )}
          <p className="entry__sep">— o —</p>
          <AnonymousButton />
        </div>
      </div>
    </>
  );
}

function LoginForm({ onSwitchToRegister }: { onSwitchToRegister: () => void }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login({ email, password });
    } catch (err) {
      setError(err instanceof ApiError ? errorText(err.codigo) : errorText(""));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h3 className="h">Iniciar sesión</h3>
      <p className="sub">Con tu cuenta @ucc.edu.ar</p>
      {error && (
        <div className="banner crit" role="alert">
          <span className="ic">!</span> {error}
        </div>
      )}
      <div className="field">
        <label htmlFor="login-email">Email institucional</label>
        <input
          id="login-email"
          className="input"
          type="email"
          placeholder="legajo@ucc.edu.ar"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />
      </div>
      <div className="field">
        <label htmlFor="login-password">Contraseña</label>
        <input
          id="login-password"
          className="input"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
      </div>
      <button type="submit" className="b b-pri" disabled={isSubmitting}>
        {isSubmitting ? "Ingresando…" : "Ingresar"}
      </button>
      <p className="entry__switch">
        ¿No tenés cuenta?{" "}
        <button type="button" className="link-btn" onClick={onSwitchToRegister}>
          Registrate
        </button>
      </p>
    </form>
  );
}

function RegisterForm({ onSwitchToLogin }: { onSwitchToLogin: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nombre, setNombre] = useState("");
  const [feedback, setFeedback] = useState<
    { kind: "ok" | "crit" | "warn"; text: string } | null
  >(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setFeedback(null);
    setIsSubmitting(true);
    try {
      const response = await registerRequest({
        email,
        password,
        nombre: nombre || null,
      });
      setFeedback({ kind: "ok", text: response.mensaje });
    } catch (err) {
      if (err instanceof ApiError && err.codigo === "AUTH_VERIFICATION_EMAIL_FAILED" && import.meta.env.DEV) {
        // Ver docs/frontend/frontend-implementation-plan.md §3.4 (FE-6) — sin
        // SMTP real configurado, register falla por completo (no se crea el
        // usuario, no queda token). No hay forma de rescatar un token de los
        // logs en este entorno; el aviso es honesto sobre esa limitación.
        setFeedback({
          kind: "warn",
          text:
            "Modo dev: no hay SMTP configurado en este entorno, así que no se pudo enviar el mail y la cuenta no se creó. " +
            "Este tramo (registro → verificación) no se puede probar localmente sin credenciales SMTP reales.",
        });
      } else {
        setFeedback({
          kind: "crit",
          text: err instanceof ApiError ? errorText(err.codigo) : errorText(""),
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h3 className="h">Crear cuenta</h3>
      <p className="sub">Con tu cuenta @ucc.edu.ar</p>
      {feedback && (
        <div className={`banner ${feedback.kind}`} role="alert">
          <span className="ic">{feedback.kind === "ok" ? "✓" : "!"}</span>{" "}
          {feedback.text}
        </div>
      )}
      <div className="field">
        <label htmlFor="register-email">Email institucional</label>
        <input
          id="register-email"
          className="input"
          type="email"
          placeholder="legajo@ucc.edu.ar"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />
      </div>
      <div className="field">
        <label htmlFor="register-password">Contraseña</label>
        <input
          id="register-password"
          className="input"
          type="password"
          minLength={8}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
      </div>
      <div className="field">
        <label htmlFor="register-nombre">Nombre (opcional)</label>
        <input
          id="register-nombre"
          className="input"
          type="text"
          value={nombre}
          onChange={(event) => setNombre(event.target.value)}
        />
      </div>
      <button type="submit" className="b b-pri" disabled={isSubmitting}>
        {isSubmitting ? "Creando cuenta…" : "Crear cuenta"}
      </button>
      <p className="entry__switch">
        ¿Ya tenés cuenta?{" "}
        <button type="button" className="link-btn" onClick={onSwitchToLogin}>
          Iniciá sesión
        </button>
      </p>
    </form>
  );
}

function AnonymousButton() {
  const { enterAnonymously } = useAuth();
  const navigate = useNavigate();

  return (
    <button
      type="button"
      className="b b-sec"
      style={{ width: "100%" }}
      onClick={() => {
        enterAnonymously();
        navigate("/config");
      }}
    >
      Entrar como anónimo (solo resultados)
    </button>
  );
}
