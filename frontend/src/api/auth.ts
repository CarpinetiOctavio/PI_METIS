import { postJson, requestJson } from "./client";
import type {
  ForgotPasswordRequest,
  LoginRequest,
  OkResponse,
  RegisterRequest,
  RegisterResponse,
  ResetPasswordRequest,
  UserMe,
  VerifyRequest,
} from "./types";

export function register(body: RegisterRequest): Promise<RegisterResponse> {
  return postJson<RegisterResponse>("/api/v1/auth/register", body);
}

export function verify(body: VerifyRequest): Promise<OkResponse> {
  return postJson<OkResponse>("/api/v1/auth/verify", body);
}

export function login(body: LoginRequest): Promise<OkResponse> {
  return postJson<OkResponse>("/api/v1/auth/login", body);
}

// DECISIÓN 085: la respuesta de forgot-password es la misma exista o no la cuenta.
export function forgotPassword(body: ForgotPasswordRequest): Promise<RegisterResponse> {
  return postJson<RegisterResponse>("/api/v1/auth/forgot-password", body);
}

export function resetPassword(body: ResetPasswordRequest): Promise<OkResponse> {
  return postJson<OkResponse>("/api/v1/auth/reset-password", body);
}

export function logout(): Promise<OkResponse> {
  return requestJson<OkResponse>("/api/v1/auth/logout", { method: "POST" });
}

export function me(): Promise<UserMe> {
  return requestJson<UserMe>("/api/v1/auth/me");
}
