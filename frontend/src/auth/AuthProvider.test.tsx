import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { AuthProvider, useAuth } from "./AuthProvider";

function Probe() {
  const { user, isAuthed, isLoading, isAnonymous, login, logout, enterAnonymously } =
    useAuth();
  return (
    <div>
      <span data-testid="loading">{String(isLoading)}</span>
      <span data-testid="authed">{String(isAuthed)}</span>
      <span data-testid="anon">{String(isAnonymous)}</span>
      <span data-testid="email">{user?.email ?? ""}</span>
      <button onClick={() => login({ email: "a@ucc.edu.ar", password: "x" })}>
        login
      </button>
      <button onClick={() => logout()}>logout</button>
      <button onClick={() => enterAnonymously()}>anon</button>
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
