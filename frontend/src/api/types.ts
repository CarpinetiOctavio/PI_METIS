// Interfaces 1:1 con el contrato real documentado en docs/frontend-integration.md
// (no con metis/schemas/analysis.py — desconectado de los endpoints reales, ver
// ese documento §5/§6). Alcance actual: solo Auth (Fase 1 del frontend).

export interface RegisterRequest {
  email: string;
  password: string;
  nombre?: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface VerifyRequest {
  token: string;
}

export interface UserMe {
  id: string;
  email: string;
  nombre: string | null;
  email_verified: boolean;
}

export interface RegisterResponse {
  ok: true;
  mensaje: string;
}

export interface OkResponse {
  ok: true;
}
