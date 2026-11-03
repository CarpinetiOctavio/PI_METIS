import { afterEach, describe, expect, it, vi } from "vitest";
import { forgotPassword, login, logout, me, register, resetPassword, verify } from "./auth";

function stubFetch(body: unknown, ok = true) {
  const fetchMock = vi.fn().mockResolvedValue({
    ok,
    status: ok ? 200 : 400,
    json: () => Promise.resolve(body),
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("api/auth", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("register posts to /api/v1/auth/register with the body", async () => {
    const fetchMock = stubFetch({ ok: true, mensaje: "Cuenta creada." });
    await register({ email: "a@ucc.edu.ar", password: "12345678", nombre: null });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/register",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ email: "a@ucc.edu.ar", password: "12345678", nombre: null }),
      }),
    );
  });

  it("verify posts the token to /api/v1/auth/verify", async () => {
    const fetchMock = stubFetch({ ok: true });
    await verify({ token: "tok123" });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/verify",
      expect.objectContaining({ method: "POST", body: JSON.stringify({ token: "tok123" }) }),
    );
  });

  it("forgotPassword posts the email to /api/v1/auth/forgot-password", async () => {
    const fetchMock = stubFetch({ ok: true, mensaje: "Revisá tu bandeja." });
    const respuesta = await forgotPassword({ email: "a@ucc.edu.ar" });

    expect(respuesta.mensaje).toBe("Revisá tu bandeja.");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/forgot-password",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ email: "a@ucc.edu.ar" }),
      }),
    );
  });

  it("resetPassword posts token and new password to /api/v1/auth/reset-password", async () => {
    const fetchMock = stubFetch({ ok: true });
    await resetPassword({ token: "tok123", password: "clave-nueva-1" });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/reset-password",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ token: "tok123", password: "clave-nueva-1" }),
      }),
    );
  });

  it("login posts credentials to /api/v1/auth/login", async () => {
    const fetchMock = stubFetch({ ok: true });
    await login({ email: "a@ucc.edu.ar", password: "12345678" });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/login",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("logout posts with no body to /api/v1/auth/logout", async () => {
    const fetchMock = stubFetch({ ok: true });
    await logout();

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/logout",
      expect.objectContaining({ method: "POST" }),
    );
    const [, init] = fetchMock.mock.calls[0];
    expect(init.body).toBeUndefined();
  });

  it("me GETs /api/v1/auth/me", async () => {
    const fetchMock = stubFetch({ id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true });
    await me();

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/me",
      expect.objectContaining({ credentials: "include" }),
    );
  });
});
