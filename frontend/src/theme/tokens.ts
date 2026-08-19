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
  glow: string;
  ok: string;
  warn: string;
  crit: string;
}

export const instrumentoTokens: { light: ThemeTokenSet; dark: ThemeTokenSet } = {
  light: {
    bg: "#EDF1F5",
    surf: "#FFFFFF",
    surf2: "#E9EEF2",
    ink: "#0B0E12",
    mut: "#5B6672",
    // H2 (plan post-avance, DECISIÓN 043) — recalculado sobre los tokens
    // actuales; ver tokens.instrumento.css y decision043.md.
    fnt: "#697888",
    line: "#D7DFE7",
    lineStrong: "#C6D0D8",
    acc: "#0E7490",
    accSoft: "#D4EEF3",
    onAcc: "#FFFFFF",
    acc2: "#4D7C0F",
    glow: "#7DD3E8",
    ok: "#0E6D3E",
    warn: "#825713",
    crit: "#A83737",
  },
  dark: {
    bg: "#090C10",
    surf: "#12171F",
    surf2: "#191F29",
    ink: "#E6EDF3",
    mut: "#8A97A6",
    fnt: "#728193",
    line: "#212A36",
    lineStrong: "#33404E",
    acc: "#22D3EE",
    accSoft: "#0C2A33",
    onAcc: "#04252B",
    acc2: "#C6F84E",
    glow: "#22D3EE",
    ok: "#35D07A",
    warn: "#F4B740",
    crit: "#FF6A6A",
  },
};
