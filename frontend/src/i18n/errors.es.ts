// Diccionario código→texto legible en español. El backend no manda mensaje
// legible en varios eventos (ver docs/frontend-implementation-plan.md §7) —
// acá solo los códigos de Auth, que es lo que necesita esta fase. Se amplía
// con los códigos de contrato/pruebas cuando el stream de Etapa 1 lo requiera.
export const ERROR_TEXT: Record<string, string> = {
  AUTH_EMAIL_ALREADY_REGISTERED: "Ese email ya está registrado.",
  AUTH_VERIFICATION_EMAIL_FAILED:
    "No pudimos enviar el mail de verificación. Probá de nuevo en unos minutos.",
  AUTH_INVALID_TOKEN: "El link de verificación es inválido o expiró.",
  AUTH_USER_NOT_FOUND: "No encontramos el usuario.",
  AUTH_INVALID_CREDENTIALS: "Email o contraseña incorrectos.",
  AUTH_EMAIL_NOT_VERIFIED: "Verificá tu email antes de iniciar sesión.",
  VALIDATION_ERROR: "Revisá los datos ingresados.",
};

const FALLBACK_TEXT = "Ocurrió un error inesperado. Probá de nuevo.";

export function errorText(codigo: string): string {
  return ERROR_TEXT[codigo] ?? FALLBACK_TEXT;
}
