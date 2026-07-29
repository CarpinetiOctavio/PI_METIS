# METIS Frontend — Fase 0 (Scaffold + Theming) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the Vite + React + TypeScript project in `frontend/`, wired with the
"Instrumento" theme (light/dark tokens), a base layout with routing stubs for the 8 chosen
wireframe screens, and a verified connectivity path to the real backend — the foundation every
later phase (auth, SSE stream, results, history, mocks) builds on.

**Architecture:** SPA built with Vite, React 18, TypeScript strict mode. Theming is pure CSS
custom properties (no CSS-in-JS runtime) toggled via `data-theme`/`data-mode` attributes on
`<html>`, read by a small React context (`ThemeProvider`) that also persists the choice.
Routing uses `react-router-dom` v6 with one stub component per screen. Backend connectivity in
dev goes through Vite's dev-server proxy (same-origin, no CORS) — see Global Constraint on CORS
below, and `docs/frontend/frontend-implementation-plan.md` §9.2.2 for why real CORS is deferred.

**Tech Stack:** Vite 5, React 18, TypeScript 5 (strict), react-router-dom 6, Vitest 2 +
React Testing Library + jsdom, ESLint 9 (flat config) + typescript-eslint.

## Global Constraints

These apply to every task in this plan — copied verbatim from
`docs/frontend/frontend-implementation-plan.md` and `docs/frontend/frontend-integration.md`.

- **Dev server port is 5173**, matching `FRONTEND_ORIGIN=http://localhost:5173` in the backend's
  `.env.example` (`docs/frontend/frontend-implementation-plan.md` §10, P2). Do not change the port without
  updating the backend `.env`.
- **CORS in dev is bypassed via a Vite proxy** (`/api` and `/ping` → `http://localhost:8000`),
  same-origin, per Decision D2 (`docs/frontend/frontend-implementation-plan.md` §9.2.2). This is a **dev-only
  shortcut** — do not implement or rely on cross-origin CORS handling in this plan; that is
  explicitly deferred to production hardening (pendiente P1). All fetch calls still set
  `credentials: "include"` so the same code works once real CORS is wired up later.
- **Theme is fixed to `data-theme="instrumento"`** (`docs/frontend/frontend-implementation-plan.md` §4).
  Only light/dark (`data-mode`) is a user toggle in this phase — no theme picker (the other three
  Fase-2 identities are not implemented; METIS ships with one theme).
- **Instrumento token values are exact** (`docs/frontend/frontend-implementation-plan.md` §4.1 /
  `frontend/frontend-design/metis-prototipo-fase3.html` `THEMES.instrumento`) — use the hex values
  and CSS variable names given in Task 3 verbatim, do not approximate or rename them.
- **Numbers render in monospace** (`--f-mono`, JetBrains Mono) — a transversal rule from Fase 2
  of the design docs. No numeric UI exists yet in Fase 0, but any numeric class/utility added here
  must default to `--f-mono`.
- **All UI copy is in Spanish** (Argentine/rioplatense) — the project is for UCC, all existing
  design docs and copy are in Spanish.
- **TypeScript strict mode**, no `any` without justification.
- **ESLint must pass clean** (`npm run lint`) — required per `.claude/rules/architecture/constraints.md`.
- **All fetch calls use `credentials: "include"`** — required for the JWT HttpOnly cookie to
  travel once auth exists (Fase 1), even though Fase 0 has no authenticated calls yet.
- Do not add CSS-in-JS libraries, UI kits (MUI, Chakra, Ant, shadcn, etc.), or state managers
  (Redux) — out of scope per `docs/frontend/frontend-implementation-plan.md` §1.1 tooling table.

---

### Task 1: Vite + React + TypeScript scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/vitest.setup.ts`
- Create: `frontend/index.html`
- Create: `frontend/.gitignore`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Test: `frontend/src/App.test.tsx`

**Interfaces:**
- Produces: `App` — default-exported React component from `frontend/src/App.tsx`, rendered into
  `#root` by `main.tsx`. Later tasks (3-7) modify `App.tsx` to add providers/router; for this task
  it renders a single `<h1>METIS</h1>`.
- Produces: dev server on port **5173** with proxy rules for `/api` and `/ping` → `http://localhost:8000`
  (see Global Constraints). Task 7 depends on this proxy existing.

- [ ] **Step 1: Create `frontend/package.json`**

```json
{
  "name": "metis-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.2"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.5.0",
    "@testing-library/react": "^16.0.1",
    "@testing-library/user-event": "^14.5.2",
    "@types/node": "^22.5.5",
    "@types/react": "^18.3.9",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "eslint": "^9.11.0",
    "eslint-plugin-react-hooks": "^4.6.2",
    "eslint-plugin-react-refresh": "^0.4.12",
    "jsdom": "^25.0.0",
    "typescript": "^5.6.2",
    "typescript-eslint": "^8.6.0",
    "vite": "^5.4.7",
    "vitest": "^2.1.1"
  }
}
```

- [ ] **Step 2: Create `frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 3: Create `frontend/tsconfig.node.json`**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 4: Create `frontend/vite.config.ts`**

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev-only CORS bypass (Decision D2, docs/frontend/frontend-implementation-plan.md §9.2.2):
// same-origin via proxy so the browser never needs cross-origin CORS in development.
// Real CORS handling for production is pendiente P1 — not implemented here.
const BACKEND_ORIGIN = "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": { target: BACKEND_ORIGIN, changeOrigin: true },
      "/ping": { target: BACKEND_ORIGIN, changeOrigin: true },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
  },
});
```

- [ ] **Step 5: Create `frontend/vitest.setup.ts`**

```ts
import "@testing-library/jest-dom/vitest";
```

- [ ] **Step 6: Create `frontend/index.html`**

```html
<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>METIS</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 7: Create `frontend/.gitignore`**

```
node_modules
dist
dist-ssr
*.local
.vite
coverage
```

- [ ] **Step 8: Create `frontend/src/App.tsx`**

```tsx
function App() {
  return <h1>METIS</h1>;
}

export default App;
```

- [ ] **Step 9: Create `frontend/src/main.tsx`**

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

- [ ] **Step 10: Write the failing test — `frontend/src/App.test.tsx`**

```tsx
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  it("renders the METIS heading", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "METIS" })).toBeInTheDocument();
  });
});
```

- [ ] **Step 11: Install dependencies**

Run: `cd frontend && npm install`
Expected: installs without error, creates `node_modules/` and `package-lock.json`.

- [ ] **Step 12: Run the test to verify it passes**

Run: `cd frontend && npm test`
Expected: `1 passed` (the test was written against the already-implemented `App.tsx`, since this
task's App is trivial — this step confirms Vitest + RTL + jsdom are wired correctly end-to-end).

- [ ] **Step 13: Verify the production build compiles**

Run: `cd frontend && npm run build`
Expected: exits 0, produces `frontend/dist/`.

- [ ] **Step 14: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/tsconfig.json frontend/tsconfig.node.json frontend/vite.config.ts frontend/vitest.setup.ts frontend/index.html frontend/.gitignore frontend/src/main.tsx frontend/src/App.tsx frontend/src/App.test.tsx
git commit -m "feat(frontend): scaffold Vite+React+TS project with dev proxy and test setup"
```

---

### Task 2: ESLint configuration

**Files:**
- Create: `frontend/eslint.config.js`
- Modify: `frontend/package.json` (no script changes needed — `lint` already points to `eslint .`
  from Task 1; this task only adds the config `eslint .` reads)

**Interfaces:**
- Consumes: the `frontend/src/**/*.{ts,tsx}` file tree produced by Task 1 (and grown by every
  later task) — `npm run lint` must stay clean as new files are added in Tasks 3-7.
- Produces: nothing later tasks import; this is tooling, not runtime code.

- [ ] **Step 1: Create `frontend/eslint.config.js`**

```js
import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist", "coverage"] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
    },
  },
);
```

- [ ] **Step 2: Add the missing dev dependencies this config needs**

`@eslint/js`, `globals`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`, and
`typescript-eslint` are already listed in Task 1's `package.json` devDependencies except
`@eslint/js` and `globals` — add them:

Edit `frontend/package.json`, in `devDependencies`, add:
```json
    "@eslint/js": "^9.11.0",
    "globals": "^15.9.0",
```

Run: `cd frontend && npm install`
Expected: installs the two new packages without error.

- [ ] **Step 3: Run lint against the Task 1 scaffold**

Run: `cd frontend && npm run lint`
Expected: exits 0, no errors or warnings against `App.tsx`, `main.tsx`, `App.test.tsx`.

If it fails, fix the reported issues in the Task 1 files (do not disable rules to silence them).

- [ ] **Step 4: Commit**

```bash
git add frontend/eslint.config.js frontend/package.json frontend/package-lock.json
git commit -m "chore(frontend): add ESLint flat config"
```

---

### Task 3: Instrumento theme tokens

**Files:**
- Create: `frontend/src/theme/tokens.instrumento.css`
- Create: `frontend/src/theme/tokens.ts`
- Test: `frontend/src/theme/tokens.test.ts`

**Interfaces:**
- Produces: `instrumentoTokens` — exported const object from `tokens.ts` with shape
  `{ light: ThemeTokenSet; dark: ThemeTokenSet }` where `ThemeTokenSet` has the keys listed in
  Step 2 below (camelCase versions of the CSS variable names, e.g. `bg`, `surf`, `acc`). Task 4
  (`ThemeProvider`) imports `instrumentoTokens` to know which keys exist, but does NOT need the
  values — it only toggles `data-theme`/`data-mode` attributes; the CSS file (not JS) is what
  actually applies colors, so `ThemeProvider` never sets `style` properties directly.
- Produces: CSS custom properties scoped under `:root[data-theme="instrumento"][data-mode="light"]`
  and `:root[data-theme="instrumento"][data-mode="dark"]`, plus theme-wide (mode-independent)
  vars under `:root[data-theme="instrumento"]`. Task 5 (`global.css`) and every component from
  Task 6 onward reads these vars via `var(--acc)`, `var(--bg)`, etc. — never hardcoded hex.

- [ ] **Step 1: Write the failing test — `frontend/src/theme/tokens.test.ts`**

```ts
import { describe, expect, it } from "vitest";
import { instrumentoTokens } from "./tokens";

describe("instrumentoTokens", () => {
  it("defines both light and dark sets with matching keys", () => {
    const lightKeys = Object.keys(instrumentoTokens.light).sort();
    const darkKeys = Object.keys(instrumentoTokens.dark).sort();
    expect(lightKeys).toEqual(darkKeys);
  });

  it("uses the exact accent color confirmed for Instrumento dark mode", () => {
    expect(instrumentoTokens.dark.acc).toBe("#22D3EE");
  });

  it("uses the exact background confirmed for Instrumento light mode", () => {
    expect(instrumentoTokens.light.bg).toBe("#F3F6F8");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- tokens.test.ts`
Expected: FAIL — `Cannot find module './tokens'` (file doesn't exist yet).

- [ ] **Step 3: Create `frontend/src/theme/tokens.ts`**

Values copied verbatim from `docs/frontend/frontend-implementation-plan.md` §4.1 /
`frontend/frontend-design/metis-prototipo-fase3.html` `THEMES.instrumento`:

```ts
export interface ThemeTokenSet {
  bg: string;
  surf: string;
  surf2: string;
  ink: string;
  mut: string;
  fnt: string;
  line: string;
  lineStrong: string;
  acc: string;
  accSoft: string;
  onAcc: string;
  acc2: string;
  ok: string;
  warn: string;
  crit: string;
}

export const instrumentoTokens: { light: ThemeTokenSet; dark: ThemeTokenSet } = {
  light: {
    bg: "#F3F6F8",
    surf: "#FFFFFF",
    surf2: "#E9EEF2",
    ink: "#0B0E12",
    mut: "#5B6672",
    fnt: "#9AA5B1",
    line: "#DEE5EB",
    lineStrong: "#C6D0D8",
    acc: "#0E7490",
    accSoft: "#D4EEF3",
    onAcc: "#FFFFFF",
    acc2: "#4D7C0F",
    ok: "#128A4E",
    warn: "#B5791A",
    crit: "#C24444",
  },
  dark: {
    bg: "#090C10",
    surf: "#12171F",
    surf2: "#191F29",
    ink: "#E6EDF3",
    mut: "#8A97A6",
    fnt: "#566270",
    line: "#212A36",
    lineStrong: "#33404E",
    acc: "#22D3EE",
    accSoft: "#0C2A33",
    onAcc: "#04252B",
    acc2: "#C6F84E",
    ok: "#35D07A",
    warn: "#F4B740",
    crit: "#FF6A6A",
  },
};
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && npm test -- tokens.test.ts`
Expected: `3 passed`.

- [ ] **Step 5: Create `frontend/src/theme/tokens.instrumento.css`**

```css
:root[data-theme="instrumento"] {
  --f-head: "JetBrains Mono", monospace;
  --f-body: "JetBrains Mono", monospace;
  --f-mono: "JetBrains Mono", monospace;
  --r-sm: 3px;
  --r-md: 4px;
}

:root[data-theme="instrumento"][data-mode="light"] {
  --bg: #f3f6f8;
  --surf: #ffffff;
  --surf2: #e9eef2;
  --ink: #0b0e12;
  --mut: #5b6672;
  --fnt: #9aa5b1;
  --line: #dee5eb;
  --line-strong: #c6d0d8;
  --acc: #0e7490;
  --acc-soft: #d4eef3;
  --on-acc: #ffffff;
  --acc2: #4d7c0f;
  --ok: #128a4e;
  --warn: #b5791a;
  --crit: #c24444;
}

:root[data-theme="instrumento"][data-mode="dark"] {
  --bg: #090c10;
  --surf: #12171f;
  --surf2: #191f29;
  --ink: #e6edf3;
  --mut: #8a97a6;
  --fnt: #566270;
  --line: #212a36;
  --line-strong: #33404e;
  --acc: #22d3ee;
  --acc-soft: #0c2a33;
  --on-acc: #04252b;
  --acc2: #c6f84e;
  --ok: #35d07a;
  --warn: #f4b740;
  --crit: #ff6a6a;
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/theme/tokens.ts frontend/src/theme/tokens.instrumento.css frontend/src/theme/tokens.test.ts
git commit -m "feat(frontend): add Instrumento theme tokens (light/dark)"
```

---

### Task 4: ThemeProvider (light/dark toggle + persistence)

**Files:**
- Create: `frontend/src/theme/ThemeProvider.tsx`
- Test: `frontend/src/theme/ThemeProvider.test.tsx`
- Modify: `frontend/src/main.tsx` — import `tokens.instrumento.css` and wrap `<App />` in
  `<ThemeProvider>`

**Interfaces:**
- Consumes: nothing from earlier tasks except the CSS file existing (Task 3) — `ThemeProvider`
  itself never reads `instrumentoTokens` values, only sets attributes.
- Produces: `ThemeProvider` (component, wraps children) and `useTheme()` hook returning
  `{ mode: "light" | "dark"; toggleMode: () => void }`. Task 6 (`TopBar`) consumes `useTheme()` for
  the theme toggle button and mode badge.
- Produces: sets `document.documentElement.dataset.theme = "instrumento"` (fixed, no setter
  exposed — per Global Constraints, theme choice is not user-facing in this phase) and
  `document.documentElement.dataset.mode = mode`.
- Produces: persists `mode` to `localStorage` under key `"metis-theme-mode"`. On first load with
  no stored value, defaults to `window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"`.

- [ ] **Step 1: Write the failing test — `frontend/src/theme/ThemeProvider.test.tsx`**

```tsx
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider, useTheme } from "./ThemeProvider";

function Consumer() {
  const { mode, toggleMode } = useTheme();
  return (
    <div>
      <span data-testid="mode">{mode}</span>
      <button onClick={toggleMode}>toggle</button>
    </div>
  );
}

describe("ThemeProvider", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
    document.documentElement.removeAttribute("data-mode");
    // jsdom's own matchMedia support for prefers-color-scheme is unreliable
    // across versions — stub it explicitly in every test so "no stored
    // preference" always exercises a known, deterministic value (light).
    vi.spyOn(window, "matchMedia").mockReturnValue({
      matches: false,
    } as MediaQueryList);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("sets data-theme to instrumento on the root element", () => {
    render(
      <ThemeProvider>
        <Consumer />
      </ThemeProvider>,
    );
    expect(document.documentElement.dataset.theme).toBe("instrumento");
  });

  it("defaults to light when there is no stored preference and no dark media match", () => {
    render(
      <ThemeProvider>
        <Consumer />
      </ThemeProvider>,
    );
    expect(screen.getByTestId("mode")).toHaveTextContent("light");
    expect(document.documentElement.dataset.mode).toBe("light");
  });

  it("toggles mode and persists the choice to localStorage", () => {
    render(
      <ThemeProvider>
        <Consumer />
      </ThemeProvider>,
    );

    fireEvent.click(screen.getByRole("button", { name: "toggle" }));

    expect(screen.getByTestId("mode")).toHaveTextContent("dark");
    expect(document.documentElement.dataset.mode).toBe("dark");
    expect(localStorage.getItem("metis-theme-mode")).toBe("dark");
  });

  it("reads a stored preference instead of the media query on mount", () => {
    localStorage.setItem("metis-theme-mode", "dark");

    render(
      <ThemeProvider>
        <Consumer />
      </ThemeProvider>,
    );

    expect(screen.getByTestId("mode")).toHaveTextContent("dark");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- ThemeProvider.test.tsx`
Expected: FAIL — `Cannot find module './ThemeProvider'`.

- [ ] **Step 3: Create `frontend/src/theme/ThemeProvider.tsx`**

```tsx
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

export type ThemeMode = "light" | "dark";

const STORAGE_KEY = "metis-theme-mode";
const THEME_NAME = "instrumento";

interface ThemeContextValue {
  mode: ThemeMode;
  toggleMode: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function readInitialMode(): ThemeMode {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark") {
    return stored;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>(readInitialMode);

  useEffect(() => {
    document.documentElement.dataset.theme = THEME_NAME;
    document.documentElement.dataset.mode = mode;
    localStorage.setItem(STORAGE_KEY, mode);
  }, [mode]);

  const toggleMode = useCallback(() => {
    setMode((current) => (current === "light" ? "dark" : "light"));
  }, []);

  return (
    <ThemeContext.Provider value={{ mode, toggleMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme debe usarse dentro de <ThemeProvider>");
  }
  return ctx;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && npm test -- ThemeProvider.test.tsx`
Expected: `4 passed`.

- [ ] **Step 5: Wire into `frontend/src/main.tsx`**

Replace the file's contents with:

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { ThemeProvider } from "./theme/ThemeProvider";
import "./theme/tokens.instrumento.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </StrictMode>,
);
```

- [ ] **Step 6: Run the full test suite and lint to confirm nothing broke**

Run: `cd frontend && npm test && npm run lint`
Expected: all tests pass, lint exits 0.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/theme/ThemeProvider.tsx frontend/src/theme/ThemeProvider.test.tsx frontend/src/main.tsx
git commit -m "feat(frontend): add ThemeProvider with light/dark toggle and persistence"
```

---

### Task 5: Instrumento global visual treatments

**Files:**
- Create: `frontend/src/theme/global.css`
- Modify: `frontend/src/main.tsx` — import `./theme/global.css` (after `tokens.instrumento.css`)

**Interfaces:**
- Consumes: CSS vars from Task 3 (`--bg`, `--ink`, `--acc`, `--line`, etc.) and the
  `data-mode`/`data-theme` attributes set by Task 4's `ThemeProvider`.
- Produces: base body styling, a `.app-shell` class (technical grid background), a `.card` class
  (HUD corner-bracket treatment via `::before`/`::after`), a `.badge-live` class (pulsing
  animation, used later for the SSE "live" indicator in Fase 2 — not consumed by any Fase 0 task,
  defined now since it belongs with the rest of the theme's identity rules), and dark-mode-only
  scanline/glow overrides. Task 6's `TopBar` uses `.app-shell` on its root wrapper.

- [ ] **Step 1: Create `frontend/src/theme/global.css`**

```css
* {
  box-sizing: border-box;
}

html,
body,
#root {
  height: 100%;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--f-body);
}

.num {
  font-family: var(--f-mono);
  font-variant-numeric: tabular-nums;
}

/* Retícula técnica de fondo — Instrumento (Fase 3, línea 143 del prototipo) */
.app-shell {
  min-height: 100%;
  background-color: var(--bg);
  background-image:
    linear-gradient(var(--line) 1px, transparent 1px),
    linear-gradient(90deg, var(--line) 1px, transparent 1px);
  background-size: 28px 28px;
}

/* Esquinas tipo corchete (HUD) en tarjetas — Instrumento (Fase 3, líneas 145-147) */
.card {
  position: relative;
  background: var(--surf);
  border: 1px solid var(--line);
  border-radius: var(--r-md);
  padding: 16px;
}

.card::before,
.card::after {
  content: "";
  position: absolute;
  width: 10px;
  height: 10px;
  border: 2px solid var(--acc);
  opacity: 0.65;
}

.card::before {
  top: -1px;
  left: -1px;
  border-right: 0;
  border-bottom: 0;
}

.card::after {
  bottom: -1px;
  right: -1px;
  border-left: 0;
  border-top: 0;
}

/* Badge que pulsa (indicador "en vivo") — Instrumento (Fase 3, línea 149) */
.badge-live {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--acc);
}

.badge-live::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--acc);
  animation: badge-pulse 1.6s ease-in-out infinite;
}

@keyframes badge-pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.35;
  }
}

/* Scanlines CRT + glow neón en modo oscuro — Instrumento (Fase 3, líneas 151-152) */
:root[data-theme="instrumento"][data-mode="dark"] .app-shell::after {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 5;
  opacity: 0.5;
  background: repeating-linear-gradient(
    0deg,
    transparent 0 2px,
    rgba(0, 0, 0, 0.06) 2px 3px
  );
}

:root[data-theme="instrumento"][data-mode="dark"] .num {
  text-shadow: 0 0 13px color-mix(in srgb, var(--acc) 55%, transparent);
}

@media (prefers-reduced-motion: reduce) {
  .badge-live::before {
    animation: none;
  }
}
```

- [ ] **Step 2: Import it in `frontend/src/main.tsx`**

Update the imports at the top of `frontend/src/main.tsx` to also include the new stylesheet,
after `tokens.instrumento.css`:

```tsx
import "./theme/tokens.instrumento.css";
import "./theme/global.css";
```

(The rest of `main.tsx` from Task 4 Step 5 is unchanged.)

- [ ] **Step 3: Run the full test suite and build to confirm nothing broke**

Run: `cd frontend && npm test && npm run build`
Expected: all tests still pass (this task adds no new test — it's pure CSS with no testable
logic), build exits 0.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/theme/global.css frontend/src/main.tsx
git commit -m "feat(frontend): add Instrumento global visual treatments (grid, HUD cards, badge pulse, dark scanlines)"
```

---

### Task 6: Router + TopBar layout + screen stubs

**Files:**
- Create: `frontend/src/routes/entry/EntryPage.tsx`
- Create: `frontend/src/routes/config/ConfigPage.tsx`
- Create: `frontend/src/routes/stream/StreamPage.tsx`
- Create: `frontend/src/routes/results/ResultsPage.tsx`
- Create: `frontend/src/routes/ranking/RankingPage.tsx`
- Create: `frontend/src/routes/design-events/DesignEventsPage.tsx`
- Create: `frontend/src/routes/history/HistoryPage.tsx`
- Create: `frontend/src/routes/auth-verify/AuthVerifyPage.tsx`
- Create: `frontend/src/components/TopBar.tsx`
- Create: `frontend/src/components/RootLayout.tsx`
- Modify: `frontend/src/App.tsx` — replace the placeholder heading with the router
- Test: `frontend/src/components/TopBar.test.tsx`
- Test: `frontend/src/App.test.tsx` — replace Task 1's test (heading no longer exists standalone)

**Interfaces:**
- Consumes: `useTheme()` from Task 4 (`TopBar` reads `mode` and calls `toggleMode`).
- Produces: `RootLayout` — the router's root element, renders `<TopBar />` + `<Outlet />` inside
  a `.app-shell` div (from Task 5's CSS). Fase 1+ tasks add `<AuthProvider>` around the router
  and real content into these page stubs — this task only establishes the routes and layout, each
  page stub renders a heading matching its screen name so navigation is verifiable now.
- Produces: routes at `/`, `/config`, `/stream`, `/results`, `/ranking`, `/design-events`,
  `/history`, `/auth/verify`. These paths are the ones later phases attach real behavior to — do
  not rename them without updating every later task's plan.

- [ ] **Step 1: Write the failing test — `frontend/src/components/TopBar.test.tsx`**

```tsx
import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider } from "../theme/ThemeProvider";
import { TopBar } from "./TopBar";

describe("TopBar", () => {
  it("shows the METIS wordmark and the current mode badge", () => {
    render(
      <ThemeProvider>
        <TopBar />
      </ThemeProvider>,
    );
    expect(screen.getByText("METIS")).toBeInTheDocument();
    expect(screen.getByTestId("mode-badge")).toBeInTheDocument();
  });

  it("toggles the mode badge text when the toggle button is clicked", () => {
    render(
      <ThemeProvider>
        <TopBar />
      </ThemeProvider>,
    );
    const badge = screen.getByTestId("mode-badge");
    const before = badge.textContent;
    fireEvent.click(screen.getByRole("button", { name: /cambiar tema/i }));
    expect(badge.textContent).not.toBe(before);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- TopBar.test.tsx`
Expected: FAIL — `Cannot find module './TopBar'`.

- [ ] **Step 3: Create `frontend/src/components/TopBar.tsx`**

```tsx
import { useTheme } from "../theme/ThemeProvider";

const MODE_LABEL: Record<"light" | "dark", string> = {
  light: "Claro",
  dark: "Oscuro",
};

export function TopBar() {
  const { mode, toggleMode } = useTheme();

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 20px",
        borderBottom: "1px solid var(--line)",
      }}
    >
      <span style={{ fontWeight: 700, letterSpacing: "0.5px" }}>METIS</span>
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <span data-testid="mode-badge">{MODE_LABEL[mode]}</span>
        <button type="button" onClick={toggleMode}>
          Cambiar tema
        </button>
      </div>
    </header>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && npm test -- TopBar.test.tsx`
Expected: `2 passed`.

- [ ] **Step 5: Create `frontend/src/components/RootLayout.tsx`**

```tsx
import { Outlet } from "react-router-dom";
import { TopBar } from "./TopBar";

export function RootLayout() {
  return (
    <div className="app-shell">
      <TopBar />
      <main style={{ padding: "20px" }}>
        <Outlet />
      </main>
    </div>
  );
}
```

- [ ] **Step 6: Create the eight page stubs**

`frontend/src/routes/entry/EntryPage.tsx`:
```tsx
export function EntryPage() {
  return <h1>Puerta de entrada</h1>;
}
```

`frontend/src/routes/config/ConfigPage.tsx`:
```tsx
export function ConfigPage() {
  return <h1>Carga y configuración</h1>;
}
```

`frontend/src/routes/stream/StreamPage.tsx`:
```tsx
export function StreamPage() {
  return <h1>Análisis en vivo</h1>;
}
```

`frontend/src/routes/results/ResultsPage.tsx`:
```tsx
export function ResultsPage() {
  return <h1>Resultados de Etapa 1</h1>;
}
```

`frontend/src/routes/ranking/RankingPage.tsx`:
```tsx
export function RankingPage() {
  return <h1>Ranking de distribuciones</h1>;
}
```

`frontend/src/routes/design-events/DesignEventsPage.tsx`:
```tsx
export function DesignEventsPage() {
  return <h1>Eventos de diseño</h1>;
}
```

`frontend/src/routes/history/HistoryPage.tsx`:
```tsx
export function HistoryPage() {
  return <h1>Historial</h1>;
}
```

`frontend/src/routes/auth-verify/AuthVerifyPage.tsx`:
```tsx
export function AuthVerifyPage() {
  return <h1>Verificando cuenta…</h1>;
}
```

- [ ] **Step 7: Replace `frontend/src/App.tsx`**

```tsx
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { RootLayout } from "./components/RootLayout";
import { EntryPage } from "./routes/entry/EntryPage";
import { ConfigPage } from "./routes/config/ConfigPage";
import { StreamPage } from "./routes/stream/StreamPage";
import { ResultsPage } from "./routes/results/ResultsPage";
import { RankingPage } from "./routes/ranking/RankingPage";
import { DesignEventsPage } from "./routes/design-events/DesignEventsPage";
import { HistoryPage } from "./routes/history/HistoryPage";
import { AuthVerifyPage } from "./routes/auth-verify/AuthVerifyPage";

const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      { path: "/", element: <EntryPage /> },
      { path: "/config", element: <ConfigPage /> },
      { path: "/stream", element: <StreamPage /> },
      { path: "/results", element: <ResultsPage /> },
      { path: "/ranking", element: <RankingPage /> },
      { path: "/design-events", element: <DesignEventsPage /> },
      { path: "/history", element: <HistoryPage /> },
      { path: "/auth/verify", element: <AuthVerifyPage /> },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
```

- [ ] **Step 8: Replace `frontend/src/App.test.tsx`**

Task 1's test asserted a bare `<h1>METIS</h1>` from `App`, which no longer exists standalone
(METIS is now in `TopBar`, and `App` renders the router starting at `/`, i.e. `EntryPage`).
Replace the file:

```tsx
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "./theme/ThemeProvider";
import App from "./App";

describe("App", () => {
  it("renders the entry page at the root route", () => {
    render(
      <ThemeProvider>
        <App />
      </ThemeProvider>,
    );
    expect(
      screen.getByRole("heading", { name: "Puerta de entrada" }),
    ).toBeInTheDocument();
    expect(screen.getByText("METIS")).toBeInTheDocument();
  });
});
```

- [ ] **Step 9: Run the full test suite, lint, and build**

Run: `cd frontend && npm test && npm run lint && npm run build`
Expected: all tests pass, lint exits 0, build exits 0.

- [ ] **Step 10: Commit**

```bash
git add frontend/src/routes frontend/src/components/TopBar.tsx frontend/src/components/TopBar.test.tsx frontend/src/components/RootLayout.tsx frontend/src/App.tsx frontend/src/App.test.tsx
git commit -m "feat(frontend): add router, TopBar layout, and stub pages for the 8 screens"
```

---

### Task 7: Backend connectivity check (API client + ping)

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/ping.ts`
- Create: `frontend/src/api/useBackendPing.ts`
- Test: `frontend/src/api/ping.test.ts`
- Test: `frontend/src/api/useBackendPing.test.tsx`
- Modify: `frontend/src/components/TopBar.tsx` — render a backend status indicator using
  `useBackendPing()`
- Modify: `frontend/src/components/TopBar.test.tsx` — account for the new indicator

**Interfaces:**
- Produces: `apiFetch(path: string, init?: RequestInit): Promise<Response>` from `client.ts` — a
  thin wrapper that always sets `credentials: "include"` and prefixes `path` with
  `import.meta.env.VITE_API_BASE ?? ""` (empty string in dev, so requests go through the Vite
  proxy from Task 1 same-origin; a real origin in a future prod build if nginx isn't fronting the
  app — see Global Constraints). **Every later phase's API modules (auth, analysis, history) must
  build on `apiFetch`, not call `fetch` directly**, so `credentials: "include"` is never
  forgotten.
- Produces: `checkBackendPing(): Promise<{ status: string }>` from `ping.ts`, calling
  `apiFetch("/ping")` and parsing the JSON body (backend returns `{"status": "ok"}` per
  `docs/frontend/frontend-integration.md` §1).
- Produces: `useBackendPing()` hook from `useBackendPing.ts` returning
  `{ state: "loading" | "ok" | "error" }`, used by `TopBar`.

- [ ] **Step 1: Write the failing test — `frontend/src/api/ping.test.ts`**

```ts
import { afterEach, describe, expect, it, vi } from "vitest";
import { checkBackendPing } from "./ping";

describe("checkBackendPing", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls /ping with credentials included and returns the parsed body", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: "ok" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await checkBackendPing();

    expect(result).toEqual({ status: "ok" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/ping",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("throws when the backend responds with a non-ok status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 500 }),
    );

    await expect(checkBackendPing()).rejects.toThrow();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- ping.test.ts`
Expected: FAIL — `Cannot find module './ping'`.

- [ ] **Step 3: Create `frontend/src/api/client.ts`**

```ts
const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export async function apiFetch(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  return fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
  });
}
```

- [ ] **Step 4: Create `frontend/src/api/ping.ts`**

```ts
import { apiFetch } from "./client";

export interface PingResponse {
  status: string;
}

export async function checkBackendPing(): Promise<PingResponse> {
  const response = await apiFetch("/ping");
  if (!response.ok) {
    throw new Error(`Backend ping falló con status ${response.status}`);
  }
  return response.json();
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd frontend && npm test -- ping.test.ts`
Expected: `2 passed`.

- [ ] **Step 6: Write the failing test — `frontend/src/api/useBackendPing.test.tsx`**

```tsx
import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { useBackendPing } from "./useBackendPing";

function Probe() {
  const { state } = useBackendPing();
  return <span data-testid="state">{state}</span>;
}

describe("useBackendPing", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("starts in loading state then resolves to ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      }),
    );

    render(<Probe />);

    expect(screen.getByTestId("state")).toHaveTextContent("loading");
    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent("ok"),
    );
  });

  it("resolves to error when the ping fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 500 }),
    );

    render(<Probe />);

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent("error"),
    );
  });
});
```

- [ ] **Step 7: Run test to verify it fails**

Run: `cd frontend && npm test -- useBackendPing.test.tsx`
Expected: FAIL — `Cannot find module './useBackendPing'`.

- [ ] **Step 8: Create `frontend/src/api/useBackendPing.ts`**

```ts
import { useEffect, useState } from "react";
import { checkBackendPing } from "./ping";

export type BackendPingState = "loading" | "ok" | "error";

export function useBackendPing(): { state: BackendPingState } {
  const [state, setState] = useState<BackendPingState>("loading");

  useEffect(() => {
    let cancelled = false;

    checkBackendPing()
      .then(() => {
        if (!cancelled) setState("ok");
      })
      .catch(() => {
        if (!cancelled) setState("error");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { state };
}
```

- [ ] **Step 9: Run test to verify it passes**

Run: `cd frontend && npm test -- useBackendPing.test.tsx`
Expected: `2 passed`.

- [ ] **Step 10: Wire the indicator into `frontend/src/components/TopBar.tsx`**

Replace the file's contents:

```tsx
import { useTheme } from "../theme/ThemeProvider";
import { useBackendPing } from "../api/useBackendPing";

const MODE_LABEL: Record<"light" | "dark", string> = {
  light: "Claro",
  dark: "Oscuro",
};

const BACKEND_LABEL: Record<"loading" | "ok" | "error", string> = {
  loading: "Conectando…",
  ok: "Backend conectado",
  error: "Backend no disponible",
};

export function TopBar() {
  const { mode, toggleMode } = useTheme();
  const { state } = useBackendPing();

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 20px",
        borderBottom: "1px solid var(--line)",
      }}
    >
      <span style={{ fontWeight: 700, letterSpacing: "0.5px" }}>METIS</span>
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <span data-testid="backend-status">{BACKEND_LABEL[state]}</span>
        <span data-testid="mode-badge">{MODE_LABEL[mode]}</span>
        <button type="button" onClick={toggleMode}>
          Cambiar tema
        </button>
      </div>
    </header>
  );
}
```

- [ ] **Step 11: Update `frontend/src/components/TopBar.test.tsx`** to stub `fetch` (the indicator
now calls the backend on mount) and assert the new element

Replace the file:

```tsx
import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider } from "../theme/ThemeProvider";
import { TopBar } from "./TopBar";

describe("TopBar", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the METIS wordmark, backend status, and mode badge", () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      }),
    );

    render(
      <ThemeProvider>
        <TopBar />
      </ThemeProvider>,
    );
    expect(screen.getByText("METIS")).toBeInTheDocument();
    expect(screen.getByTestId("backend-status")).toBeInTheDocument();
    expect(screen.getByTestId("mode-badge")).toBeInTheDocument();
  });

  it("toggles the mode badge text when the toggle button is clicked", () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      }),
    );

    render(
      <ThemeProvider>
        <TopBar />
      </ThemeProvider>,
    );
    const badge = screen.getByTestId("mode-badge");
    const before = badge.textContent;
    fireEvent.click(screen.getByRole("button", { name: /cambiar tema/i }));
    expect(badge.textContent).not.toBe(before);
  });
});
```

- [ ] **Step 12: Run the full test suite, lint, and build**

Run: `cd frontend && npm test && npm run lint && npm run build`
Expected: all tests pass, lint exits 0, build exits 0.

- [ ] **Step 13: Commit**

```bash
git add frontend/src/api/client.ts frontend/src/api/ping.ts frontend/src/api/useBackendPing.ts frontend/src/api/ping.test.ts frontend/src/api/useBackendPing.test.tsx frontend/src/components/TopBar.tsx frontend/src/components/TopBar.test.tsx
git commit -m "feat(frontend): add typed API client and backend connectivity indicator"
```

---

## End-of-phase manual verification (not a subagent task — controller/human checklist)

After Task 7's review is approved, the plan's automated tasks are done, but Fase 0's own
"hecho si" criteria (`docs/frontend/frontend-implementation-plan.md`, Fase 0) include a live check that no
subagent can perform meaningfully (a dev server + real browser + real backend):

1. Start the real backend (`docker-compose up backend postgres` or `uvicorn metis.main:app --reload
   --port 8000` per `docs/frontend/frontend-integration.md` §1).
2. Run `cd frontend && npm run dev` — confirm it serves on `http://localhost:5173`.
3. Open it in a browser: confirm the entry page renders, the theme toggle switches all tokens
   (background, ink, accent visibly change), and the TopBar's backend status reads "Backend
   conectado" (proving the `/ping` proxy path works end-to-end against the real backend, not a
   mock).
4. Navigate directly to each of the 8 routes (`/config`, `/stream`, `/results`, `/ranking`,
   `/design-events`, `/history`, `/auth/verify`) and confirm each stub renders without a router
   error.
