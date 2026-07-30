const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export async function apiFetch(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  return fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
  });
}

// Body real de error de la app: { error: { codigo, mensaje } } (ver
// .claude/rules/architecture/api-contracts.md — "Estructura de error estándar").
interface AppErrorBody {
  error: { codigo: string; mensaje: string };
}

// Body de error 422 de Pydantic/FastAPI — shape distinto, no pasa por AppErrorBody
// (ver docs/frontend-integration.md §2 — register valida email/password a nivel
// Pydantic y responde 422, no 400).
interface PydanticErrorBody {
  detail: Array<{ loc: unknown[]; msg: string; type: string }>;
}

export class ApiError extends Error {
  readonly status: number;
  readonly codigo: string;

  constructor(status: number, codigo: string, mensaje: string) {
    super(mensaje);
    this.name = "ApiError";
    this.status = status;
    this.codigo = codigo;
  }
}

function isAppErrorBody(body: unknown): body is AppErrorBody {
  return (
    typeof body === "object" &&
    body !== null &&
    "error" in body &&
    typeof (body as AppErrorBody).error?.codigo === "string"
  );
}

function isPydanticErrorBody(body: unknown): body is PydanticErrorBody {
  return (
    typeof body === "object" &&
    body !== null &&
    Array.isArray((body as PydanticErrorBody).detail)
  );
}

async function toApiError(response: Response): Promise<ApiError> {
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    return new ApiError(
      response.status,
      "UNKNOWN_ERROR",
      `Error inesperado del servidor (status ${response.status}).`,
    );
  }

  if (response.status === 422 && isPydanticErrorBody(body)) {
    const [first] = body.detail;
    return new ApiError(
      422,
      "VALIDATION_ERROR",
      first?.msg ?? "Los datos enviados no son válidos.",
    );
  }

  if (isAppErrorBody(body)) {
    return new ApiError(response.status, body.error.codigo, body.error.mensaje);
  }

  return new ApiError(
    response.status,
    "UNKNOWN_ERROR",
    `Error inesperado del servidor (status ${response.status}).`,
  );
}

/** fetch + parseo JSON tipado; lanza ApiError normalizado ante cualquier status no-ok. */
export async function requestJson<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await apiFetch(path, init);
  if (!response.ok) {
    throw await toApiError(response);
  }
  return response.json() as Promise<T>;
}

/** Azúcar sobre requestJson para POSTs con body JSON (todos los endpoints de auth). */
export function postJson<T>(path: string, body: unknown): Promise<T> {
  return requestJson<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
