import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import * as authApi from "../api/auth";
import { ApiError } from "../api/client";
import { errorText } from "../i18n/errors.es";
import type { LoginRequest, UserMe } from "../api/types";

const ANON_STORAGE_KEY = "metis-anon-session";

interface AuthContextValue {
  user: UserMe | null;
  isAuthed: boolean;
  isLoading: boolean;
  isAnonymous: boolean;
  login: (body: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  enterAnonymously: () => void;
  refetch: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: Readonly<{ children: ReactNode }>) {
  const [user, setUser] = useState<UserMe | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnonymous, setIsAnonymous] = useState(
    () => localStorage.getItem(ANON_STORAGE_KEY) === "true",
  );

  // Espejo síncrono de `user`, actualizado dentro de refetch() mismo (no en
  // un efecto) — login() necesita saber si la sesión quedó abierta
  // inmediatamente después de esperar refetch(), y el estado de React no se
  // actualiza sincrónicamente con el setUser de más abajo.
  const userRef = useRef<UserMe | null>(null);

  const refetch = useCallback(async () => {
    try {
      const currentUser = await authApi.me();
      userRef.current = currentUser;
      setUser(currentUser);
    } catch (err) {
      userRef.current = null;
      if (err instanceof ApiError && err.status === 401) {
        // Sin cookie: no hay sesión, estado normal, no es un error real.
        setUser(null);
        return;
      }
      // Red caída, CORS, 500 — F3 (informe-diagnostico-ui-rota.md): antes
      // este catch colapsaba estos casos junto al 401 legítimo, y como
      // login() no verificaba el resultado, un fallo acá se veía desde la
      // UI como "aprieto el botón y no pasa nada". El llamador tiene que
      // enterarse.
      setUser(null);
      throw err;
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        await refetch();
      } catch {
        // Backend caído / CORS en el arranque — TopBar ya informa ese
        // estado independientemente vía useBackendPing. Acá solo evitamos
        // que la carga inicial quede colgada en el spinner para siempre.
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(
    async (body: LoginRequest) => {
      await authApi.login(body);
      await refetch(); // ahora sí puede lanzar (red caída, CORS, 500)
      if (!userRef.current) {
        // POST /auth/login respondió 200 pero GET /auth/me no confirmó la
        // sesión — F3: antes login() resolvía igual, sin lanzar.
        throw new ApiError(
          0,
          "SESSION_NOT_ESTABLISHED",
          errorText("SESSION_NOT_ESTABLISHED"),
        );
      }
      localStorage.removeItem(ANON_STORAGE_KEY);
      setIsAnonymous(false);
    },
    [refetch],
  );

  const logout = useCallback(async () => {
    await authApi.logout();
    setUser(null);
    // D8 (pasada de mejora): antes no limpiaba el flag anónimo — un usuario
    // que hizo login real y después logout podía quedar con
    // metis-anon-session="true" residual de una sesión anónima anterior.
    localStorage.removeItem(ANON_STORAGE_KEY);
    setIsAnonymous(false);
  }, []);

  const enterAnonymously = useCallback(() => {
    localStorage.setItem(ANON_STORAGE_KEY, "true");
    setIsAnonymous(true);
  }, []);

  // R2 (limpieza SonarCloud): sin useMemo, este objeto se recrea en cada
  // render de AuthProvider — y como envuelve toda la app, eso significa que
  // cada pantalla re-renderiza aunque nada haya cambiado. Las funciones ya
  // están en useCallback con deps estables, así que el array de abajo es
  // seguro tal como lo valida react-hooks/exhaustive-deps.
  const value = useMemo(
    () => ({
      user,
      isAuthed: user !== null,
      isLoading,
      isAnonymous,
      login,
      logout,
      enterAnonymously,
      refetch,
    }),
    [user, isLoading, isAnonymous, login, logout, enterAnonymously, refetch],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  }
  return ctx;
}
