import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, vi } from "vitest";

// jsdom does not implement matchMedia. ThemeProvider calls it unconditionally
// on mount (to read the prefers-color-scheme media query), so every test that
// renders <ThemeProvider> — directly or via <App>/<TopBar> — needs a
// deterministic stub. Defined once here instead of duplicated per test file.
beforeEach(() => {
  vi.spyOn(window, "matchMedia").mockReturnValue({
    matches: false,
  } as MediaQueryList);
});

afterEach(() => {
  vi.restoreAllMocks();
});
