import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { instrumentoTokens, type ThemeTokenSet } from "./tokens";

// tokens.ts (instrumentoTokens) and tokens.instrumento.css hand-duplicate the
// same 30 hex values with nothing detecting drift between them. This test
// parses the CSS custom properties out of the [data-mode="light"] and
// [data-mode="dark"] blocks and asserts every key in instrumentoTokens has a
// matching CSS variable with the same hex value.
//
// NOTE: `new URL("./x", import.meta.url)` is deliberately avoided here — under
// Vitest's jsdom environment the global `URL` constructor resolves relative
// paths against the jsdom document location (http://localhost:3000/...)
// instead of the file:// base, silently producing the wrong path. Resolving
// via node:path against this file's own directory sidesteps that.
const selfPath = fileURLToPath(import.meta.url);
const cssPath = path.join(path.dirname(selfPath), "tokens.instrumento.css");
const css = readFileSync(cssPath, "utf-8");

function extractModeBlock(mode: "light" | "dark"): string {
  const blockRegex = new RegExp(
    `\\[data-mode="${mode}"\\]\\s*\\{([^}]*)\\}`,
  );
  const match = css.match(blockRegex);
  if (!match) {
    throw new Error(
      `Could not find [data-mode="${mode}"] block in tokens.instrumento.css`,
    );
  }
  return match[1];
}

function extractCssVars(block: string): Record<string, string> {
  const vars: Record<string, string> = {};
  const declRegex = /--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]+)\s*;/g;
  let decl: RegExpExecArray | null;
  while ((decl = declRegex.exec(block)) !== null) {
    vars[decl[1]] = decl[2].toLowerCase();
  }
  return vars;
}

// camelCase -> kebab-case, matching the convention used in the CSS file:
// acc2 -> --acc2, lineStrong -> --line-strong, onAcc -> --on-acc,
// accSoft -> --acc-soft.
function toCssVarName(key: string): string {
  return key.replace(/([A-Z])/g, "-$1").toLowerCase();
}

describe("instrumentoTokens / tokens.instrumento.css parity", () => {
  const lightVars = extractCssVars(extractModeBlock("light"));
  const darkVars = extractCssVars(extractModeBlock("dark"));

  it("parsed a non-trivial number of variables from each CSS block", () => {
    // sanity check that the regex-based parsing above actually found
    // something — guards against a silently-vacuous test.
    expect(Object.keys(lightVars).length).toBeGreaterThan(0);
    expect(Object.keys(darkVars).length).toBeGreaterThan(0);
  });

  it.each(Object.keys(instrumentoTokens.light) as Array<keyof ThemeTokenSet>)(
    "light.%s matches --%s in the CSS light block",
    (key) => {
      const cssVarName = toCssVarName(key);
      expect(lightVars[cssVarName]).toBeDefined();
      expect(lightVars[cssVarName]).toBe(
        instrumentoTokens.light[key].toLowerCase(),
      );
    },
  );

  it.each(Object.keys(instrumentoTokens.dark) as Array<keyof ThemeTokenSet>)(
    "dark.%s matches --%s in the CSS dark block",
    (key) => {
      const cssVarName = toCssVarName(key);
      expect(darkVars[cssVarName]).toBeDefined();
      expect(darkVars[cssVarName]).toBe(
        instrumentoTokens.dark[key].toLowerCase(),
      );
    },
  );
});
