import { postJson, requestJson } from "./client";
import type {
  LoginRequest,
  OkResponse,
  RegisterRequest,
  RegisterResponse,
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

export function logout(): Promise<OkResponse> {
  return requestJson<OkResponse>("/api/v1/auth/logout", { method: "POST" });
}

export function me(): Promise<UserMe> {
  return requestJson<UserMe>("/api/v1/auth/me");
}
