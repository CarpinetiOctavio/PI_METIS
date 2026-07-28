import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ThemeProvider } from "../theme/ThemeProvider";
import { AuthProvider } from "../auth/AuthProvider";
import { TopBar } from "./TopBar";

function stubFetch(
  meResponse: { ok: boolean; status?: number; body: unknown } = {
    ok: false,
    status: 401,
    body: {},
  },
) {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.includes("/auth/me")) {
        return Promise.resolve({
          ok: meResponse.ok,
          status: meResponse.status ?? (meResponse.ok ? 200 : 401),
          json: () => Promise.resolve(meResponse.body),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      });
    }),
  );
}

function renderTopBar() {
  return render(
    <ThemeProvider>
      <AuthProvider>
        <TopBar />
      </AuthProvider>
    </ThemeProvider>,
  );
}

describe("TopBar", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the METIS wordmark, backend status, and mode badge", async () => {
    stubFetch();

    renderTopBar();
    expect(screen.getByText("METIS")).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
    expect(screen.getByTestId("mode-badge")).toBeInTheDocument();
  });

  it("toggles the mode badge text when the toggle button is clicked", async () => {
    stubFetch();

    renderTopBar();
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
    const badge = screen.getByTestId("mode-badge");
    const before = badge.textContent;
    fireEvent.click(screen.getByRole("button", { name: /cambiar tema/i }));
    expect(badge.textContent).not.toBe(before);
  });

  it("does not show the email or logout button when there is no session", async () => {
    stubFetch();

    renderTopBar();
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
    expect(screen.queryByTestId("user-email")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Cerrar sesión" }),
    ).not.toBeInTheDocument();
  });

  it("shows the user's email and a logout button when authenticated", async () => {
    stubFetch({
      ok: true,
      body: { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true },
    });

    renderTopBar();
    await waitFor(() =>
      expect(screen.getByTestId("user-email")).toHaveTextContent("a@ucc.edu.ar"),
    );
    expect(
      screen.getByRole("button", { name: "Cerrar sesión" }),
    ).toBeInTheDocument();
  });
});
