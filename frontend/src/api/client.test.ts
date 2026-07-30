import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, postJson, requestJson } from "./client";

describe("requestJson", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns the parsed body when the response is ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ id: "1" }),
      }),
    );

    await expect(requestJson("/api/v1/auth/me")).resolves.toEqual({ id: "1" });
  });

  it("throws an ApiError built from the standard { error: { codigo, mensaje } } body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        json: () =>
          Promise.resolve({
            error: { codigo: "AUTH_INVALID_CREDENTIALS", mensaje: "Email o contraseña incorrectos" },
          }),
      }),
    );

    const error = await requestJson("/api/v1/auth/login").catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({
      status: 401,
      codigo: "AUTH_INVALID_CREDENTIALS",
      message: "Email o contraseña incorrectos",
    });
  });

  it("parses the FastAPI/Pydantic 422 shape separately from the standard error body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: () =>
          Promise.resolve({
            detail: [{ loc: ["body", "email"], msg: "value is not a valid email address", type: "value_error" }],
          }),
      }),
    );

    const error = await requestJson("/api/v1/auth/register").catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({
      status: 422,
      codigo: "VALIDATION_ERROR",
      message: "value is not a valid email address",
    });
  });

  it("falls back to UNKNOWN_ERROR when the error body cannot be parsed as JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error("not json")),
      }),
    );

    const error = await requestJson("/api/v1/auth/register").catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 500, codigo: "UNKNOWN_ERROR" });
  });
});

describe("postJson", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends a JSON POST with credentials included", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ ok: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await postJson("/api/v1/auth/login", { email: "a@ucc.edu.ar", password: "12345678" });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/login",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "a@ucc.edu.ar", password: "12345678" }),
        credentials: "include",
      }),
    );
  });
});
