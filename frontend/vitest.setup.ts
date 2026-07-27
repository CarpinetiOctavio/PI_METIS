import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, vi } from "vitest";

// jsdom does not implement matchMedia. ThemeProvider calls it unconditionally
// on mount (to read the prefers-color-scheme media query), so every test that
// renders <ThemeProvider> — directly or via <App>/<TopBar> — needs a
// deterministic stub. Defined once here instead of duplicated per test file.
//
// ThemeProvider also persists metis-theme-mode to localStorage and sets
// data-theme/data-mode on <html> on every mount. Without resetting those here,
// tests in the same file (or across files sharing jsdom's window) can leak
// mode state into each other — clearing localStorage and the attributes
// before every test guarantees real isolation, not just assertion-order luck.
beforeEach(() => {
  vi.spyOn(window, "matchMedia").mockReturnValue({
    matches: false,
  } as MediaQueryList);
  localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
  document.documentElement.removeAttribute("data-mode");
});

afterEach(() => {
  vi.restoreAllMocks();
});
