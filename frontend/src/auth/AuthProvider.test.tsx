import { afterEach, describe, expect, it, vi } from "vitest";
import { useState } from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { AuthProvider, useAuth } from "./AuthProvider";
import { ApiError } from "../api/client";

function Probe() {
  const {
    user,
    isAuthed,
    isLoading,
    isAnonymous,
    login,
    logout,
    enterAnonymously,
    refetch,
  } = useAuth();
  // F3 (informe-diagnostico-ui-rota.md): login()/refetch() ahora pueden
  // lanzar en vez de fallar en silencio — el Probe necesita un lugar donde
  // capturar y mostrar ese rechazo, igual que lo haría un componente real.
  const [caught, setCaught] = useState<string>("");
  return (
    <div>
      <span data-testid="loading">{String(isLoading)}</span>
      <span data-testid="authed">{String(isAuthed)}</span>
      <span data-testid="anon">{String(isAnonymous)}</span>
      <span data-testid="email">{user?.email ?? ""}</span>
      <span data-testid="caught">{caught}</span>
      <button
        onClick={() =>
          login({ email: "a@ucc.edu.ar", password: "x" }).catch((err: unknown) =>
            setCaught(err instanceof ApiError ? err.codigo : "unknown"),
          )
        }
      >
        login
      </button>
      <button onClick={() => logout()}>logout</button>
      <button onClick={() => enterAnonymously()}>anon</button>
      <button
        onClick={() =>
          refetch().catch((err: unknown) =>
            setCaught(err instanceof Error ? err.message : "unknown"),
          )
        }
      >
        refetch
      </button>
    </div>
  );
}

function stubFetchSequence(
  responses: Record<string, { ok: boolean; status?: number; body: unknown }>,
) {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input.toString();
      const match = Object.entries(responses).find(([key]) => url.includes(key));
      if (!match) throw new Error(`unstubbed fetch: ${url}`);
      const [, res] = match;
      return Promise.resolve({
        ok: res.ok,
        status: res.status ?? (res.ok ? 200 : 400),
        json: () => Promise.resolve(res.body),
      });
    }),
  );
}

describe("AuthProvider", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it("starts loading, then resolves to unauthenticated on a 401 from /me", async () => {
    stubFetchSequence({ "/auth/me": { ok: false, status: 401, body: {} } });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    expect(screen.getByTestId("loading")).toHaveTextContent("true");
    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );
    expect(screen.getByTestId("authed")).toHaveTextContent("false");
  });

  it("resolves to authenticated when /me returns a user", async () => {
    stubFetchSequence({
      "/auth/me": {
        ok: true,
        body: { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true },
      },
    });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("authed")).toHaveTextContent("true"),
    );
    expect(screen.getByTestId("email")).toHaveTextContent("a@ucc.edu.ar");
  });

  it("login() calls /login then refetches /me, flipping isAuthed", async () => {
    let meCallCount = 0;
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = typeof input === "string" ? input : input.toString();
        if (url.includes("/auth/login")) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve({ ok: true }),
          });
        }
        if (url.includes("/auth/me")) {
          meCallCount += 1;
          const authed = meCallCount > 1;
          return Promise.resolve({
            ok: authed,
            status: authed ? 200 : 401,
            json: () =>
              Promise.resolve(
                authed
                  ? { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true }
                  : {},
              ),
          });
        }
        throw new Error(`unstubbed fetch: ${url}`);
      }),
    );

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );
    expect(screen.getByTestId("authed")).toHaveTextContent("false");

    fireEvent.click(screen.getByText("login"));

    await waitFor(() =>
      expect(screen.getByTestId("authed")).toHaveTextContent("true"),
    );
  });

  it("logout() clears the user", async () => {
    stubFetchSequence({
      "/auth/logout": { ok: true, body: { ok: true } },
      "/auth/me": {
        ok: true,
        body: { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true },
      },
    });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("authed")).toHaveTextContent("true"),
    );

    fireEvent.click(screen.getByText("logout"));

    await waitFor(() =>
      expect(screen.getByTestId("authed")).toHaveTextContent("false"),
    );
  });

  // D8 (pasada de mejora): logout() no limpiaba el flag anónimo residual —
  // un usuario que entró anónimo, después inició sesión real, y volvió a
  // hacer logout, quedaba con metis-anon-session="true" en localStorage.
  it("logout() also clears a residual anonymous session flag", async () => {
    localStorage.setItem("metis-anon-session", "true");
    stubFetchSequence({
      "/auth/logout": { ok: true, body: { ok: true } },
      "/auth/me": {
        ok: true,
        body: { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true },
      },
    });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("authed")).toHaveTextContent("true"),
    );
    expect(screen.getByTestId("anon")).toHaveTextContent("true");

    fireEvent.click(screen.getByText("logout"));

    await waitFor(() =>
      expect(screen.getByTestId("anon")).toHaveTextContent("false"),
    );
    expect(localStorage.getItem("metis-anon-session")).toBeNull();
  });

  // F3 (informe-diagnostico-ui-rota.md): antes el catch de refetch() colapsaba
  // un 401 legítimo (sin sesión) y un fallo real (red caída, CORS, 500) en el
  // mismo `setUser(null)` silencioso. Ahora solo el 401 se traga.
  it("refetch() swallows a 401 — no session is a normal outcome, not an error", async () => {
    stubFetchSequence({ "/auth/me": { ok: false, status: 401, body: {} } });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );

    fireEvent.click(screen.getByText("refetch"));

    await waitFor(() => expect(screen.getByTestId("authed")).toHaveTextContent("false"));
    expect(screen.getByTestId("caught")).toHaveTextContent("");
  });

  it("refetch() rejects on a non-401 failure instead of hiding it as 'no session'", async () => {
    stubFetchSequence({ "/auth/me": { ok: false, status: 500, body: {} } });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );

    fireEvent.click(screen.getByText("refetch"));

    await waitFor(() => expect(screen.getByTestId("caught")).not.toHaveTextContent(""));
    expect(screen.getByTestId("authed")).toHaveTextContent("false");
  });

  // F3: antes login() resolvía igual aunque /me post-login no confirmara la
  // sesión (login 200 pero el cliente termina sin cookie/sesión real) — la
  // UI se veía como "aprieto el botón y no pasa nada". Ahora login() rechaza
  // con un código propio que el llamador puede mostrar. Nota: acá /me
  // responde 401 (no 500) a propósito — refetch() trata un 401 como "no hay
  // sesión" y no lanza; es login() quien decide que eso es un fallo porque
  // ocurrió justo después de un login supuestamente exitoso.
  it("login() throws SESSION_NOT_ESTABLISHED when /login succeeds but /me can't confirm the session", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = typeof input === "string" ? input : input.toString();
        if (url.includes("/auth/login")) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve({ ok: true }),
          });
        }
        if (url.includes("/auth/me")) {
          return Promise.resolve({
            ok: false,
            status: 401,
            json: () => Promise.resolve({}),
          });
        }
        throw new Error(`unstubbed fetch: ${url}`);
      }),
    );

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );

    fireEvent.click(screen.getByText("login"));

    await waitFor(() =>
      expect(screen.getByTestId("caught")).toHaveTextContent("SESSION_NOT_ESTABLISHED"),
    );
    expect(screen.getByTestId("authed")).toHaveTextContent("false");
  });

  it("enterAnonymously() sets isAnonymous and persists it to localStorage", async () => {
    stubFetchSequence({ "/auth/me": { ok: false, status: 401, body: {} } });

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("loading")).toHaveTextContent("false"),
    );

    fireEvent.click(screen.getByText("anon"));

    expect(screen.getByTestId("anon")).toHaveTextContent("true");
    expect(localStorage.getItem("metis-anon-session")).toBe("true");
  });
});
