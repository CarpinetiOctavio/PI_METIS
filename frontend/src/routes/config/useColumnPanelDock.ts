import { useCallback, useEffect, useState } from "react";

// Bloque E (plan post-avance) — persistencia de posición de acople, ancho/alto
// y abierto/cerrado del panel de columnas. Mismo patrón que MotionProvider
// (leer una vez al montar, reescribir localStorage en cada cambio) — acá sin
// Context porque ConfigPage es el único consumidor.
export type PanelDock = "right" | "left" | "bottom";

const STORAGE_KEY = "metis-column-panel";
const DOCKS: readonly PanelDock[] = ["right", "left", "bottom"];

const DEFAULT_SIZE: Record<PanelDock, number> = {
  right: 420,
  left: 420,
  bottom: 260,
};

// right/left redimensionan ancho; bottom redimensiona alto — límites
// distintos porque son magnitudes distintas de la pantalla.
export const SIZE_LIMITS: Record<PanelDock, { min: number; max: number }> = {
  right: { min: 260, max: 720 },
  left: { min: 260, max: 720 },
  bottom: { min: 160, max: 480 },
};

export const RESIZE_KEYBOARD_STEP = 16;

interface StoredState {
  dock: PanelDock;
  open: boolean;
  size: Partial<Record<PanelDock, number>>;
}

const DEFAULT_STATE: StoredState = { dock: "right", open: true, size: {} };

function isDock(value: unknown): value is PanelDock {
  return typeof value === "string" && (DOCKS as readonly string[]).includes(value);
}

function readInitialState(): StoredState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_STATE;
    const parsed = JSON.parse(raw) as Partial<StoredState>;
    return {
      dock: isDock(parsed.dock) ? parsed.dock : DEFAULT_STATE.dock,
      open: typeof parsed.open === "boolean" ? parsed.open : DEFAULT_STATE.open,
      size:
        typeof parsed.size === "object" && parsed.size !== null
          ? parsed.size
          : {},
    };
  } catch {
    return DEFAULT_STATE;
  }
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export interface ColumnPanelDockState {
  dock: PanelDock;
  open: boolean;
  size: number;
  limits: { min: number; max: number };
  setDock: (dock: PanelDock) => void;
  setOpen: (open: boolean) => void;
  setSize: (size: number) => void;
}

export function useColumnPanelDock(): ColumnPanelDockState {
  const [state, setState] = useState<StoredState>(readInitialState);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  const setDock = useCallback((dock: PanelDock) => {
    setState((prev) => ({ ...prev, dock }));
  }, []);

  const setOpen = useCallback((open: boolean) => {
    setState((prev) => ({ ...prev, open }));
  }, []);

  const setSize = useCallback((size: number) => {
    setState((prev) => ({ ...prev, size: { ...prev.size, [prev.dock]: size } }));
  }, []);

  const limits = SIZE_LIMITS[state.dock];
  const size = clamp(state.size[state.dock] ?? DEFAULT_SIZE[state.dock], limits.min, limits.max);

  return { dock: state.dock, open: state.open, size, limits, setDock, setOpen, setSize };
}
