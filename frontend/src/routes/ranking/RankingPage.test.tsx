import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route, useLocation } from "react-router-dom";
import { RankingPage } from "./RankingPage";

function DesignEventsProbe() {
  const location = useLocation();
  return <pre data-testid="design-events-state">{JSON.stringify(location.state)}</pre>;
}

function renderRankingPage() {
  return render(
    <MemoryRouter initialEntries={["/ranking"]}>
      <Routes>
        <Route path="/ranking" element={<RankingPage />} />
        <Route path="/design-events" element={<DesignEventsProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("RankingPage", () => {
  it("renders the mock ranking with the PendingBadge visible", () => {
    renderRankingPage();
    expect(screen.getByText("pendiente · datos de ejemplo")).toBeInTheDocument();
    expect(screen.getByText("Gumbel")).toBeInTheDocument();
    expect(screen.getByText("GVE")).toBeInTheDocument();
    expect(screen.getByText("Gamma 2p")).toBeInTheDocument();
  });

  it("never labels a distribution as óptima/recomendada/ganadora — only reports 'menor EEA' as a fact", () => {
    renderRankingPage();
    const text = document.body.textContent ?? "";
    expect(text).not.toMatch(/óptima|recomendada|ganadora|mejor distribución/i);
    expect(screen.getByText("menor EEA")).toBeInTheDocument();
  });

  it("shows the calendario/hidrológico toggle on each card", () => {
    renderRankingPage();
    expect(
      screen.getAllByRole("button", { name: "Calendario" }).length,
    ).toBeGreaterThan(0);
    expect(
      screen.getAllByRole("button", { name: "Hidrológico" }).length,
    ).toBeGreaterThan(0);
  });

  it("navigates to /design-events with the chosen distribucion/metodo when Elegir is clicked", () => {
    renderRankingPage();
    const elegirButtons = screen.getAllByRole("button", { name: "Elegir" });
    fireEvent.click(elegirButtons[0]);

    const state = JSON.parse(
      screen.getByTestId("design-events-state").textContent ?? "null",
    );
    expect(state).toEqual({ distribucion: "Gumbel", metodo: "Momentos" });
  });
});
