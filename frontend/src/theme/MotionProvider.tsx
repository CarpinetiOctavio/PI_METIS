import {
  createContext,
  useCallback,
  useContext,
  useLayoutEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { prefersReducedMotion, resolveMotionLevel, type MotionLevel } from "./motion";

export type { MotionLevel };

const STORAGE_KEY = "metis-motion-level";
const LEVELS: readonly MotionLevel[] = ["alta", "media", "off"];

function isMotionLevel(value: string | null): value is MotionLevel {
  return value !== null && (LEVELS as readonly string[]).includes(value);
}

function readInitialLevel(): MotionLevel {
  const stored = localStorage.getItem(STORAGE_KEY);
  return isMotionLevel(stored) ? stored : "alta";
}

interface MotionContextValue {
  /** Lo que el usuario eligió, persistido — puede seguir en "alta" aunque
   * `effectiveLevel` sea "off" porque el sistema operativo lo fuerza. */
  level: MotionLevel;
  /** `level`, salvo que el sistema operativo pida movimiento reducido —
   * esto es lo que deben leer los componentes que deciden qué animar. */
  effectiveLevel: MotionLevel;
  setLevel: (level: MotionLevel) => void;
  /** Para que el selector pueda explicarlo ("tu sistema pide movimiento
   * reducido") en vez de aplicarlo en silencio y dejar el control como si
   * no hiciera nada. */
  systemForcesReduced: boolean;
}

// Default sin <MotionProvider> — a diferencia de useTheme() (un solo
// consumidor, TopBar), useMotion() lo leen ampliamente SpotlightCard/
// Magnet/SpecularHighlight y los tres fondos animados: exigir el provider
// en cada test que los toque (docenas de archivos en toda la suite, la
// mayoría sin ningún interés en probar niveles de movimiento) sería una
// superficie de rotura enorme por una preferencia que, sin proveedor, debe
// comportarse exactamente igual que antes de que este feature existiera:
// "alta", sin restricciones. La app real siempre tiene el provider
// (main.tsx) — este default solo importa en aislamiento (tests, Storybook
// si existiera).
const DEFAULT_VALUE: MotionContextValue = {
  level: "alta",
  effectiveLevel: "alta",
  setLevel: () => {},
  systemForcesReduced: false,
};

const MotionContext = createContext<MotionContextValue | null>(null);

export function MotionProvider({ children }: Readonly<{ children: ReactNode }>) {
  const [level, setLevel] = useState<MotionLevel>(readInitialLevel);
  const effectiveLevel = resolveMotionLevel(level);
  const systemForcesReduced = prefersReducedMotion();

  useLayoutEffect(() => {
    document.documentElement.dataset.motion = effectiveLevel;
    localStorage.setItem(STORAGE_KEY, level);
  }, [level, effectiveLevel]);

  const setLevelCallback = useCallback((next: MotionLevel) => {
    setLevel(next);
  }, []);

  const value = useMemo(
    () => ({ level, effectiveLevel, setLevel: setLevelCallback, systemForcesReduced }),
    [level, effectiveLevel, setLevelCallback, systemForcesReduced],
  );

  return <MotionContext.Provider value={value}>{children}</MotionContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useMotion(): MotionContextValue {
  const ctx = useContext(MotionContext);
  return ctx ?? DEFAULT_VALUE;
}
