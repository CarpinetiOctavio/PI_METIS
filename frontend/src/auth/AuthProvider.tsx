import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import * as authApi from "../api/auth";
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

  const refetch = useCallback(async () => {
    try {
      const currentUser = await authApi.me();
      setUser(currentUser);
    } catch {
      // 401 (sin cookie) o error de red — ambos significan "no autenticado"
      // para efectos de esta fase, ver frontend-implementation-plan.md §3.1.
      setUser(null);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      await refetch();
      if (!cancelled) setIsLoading(false);
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(
    async (body: LoginRequest) => {
      await authApi.login(body);
      await refetch();
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

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthed: user !== null,
        isLoading,
        isAnonymous,
        login,
        logout,
        enterAnonymously,
        refetch,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  }
  return ctx;
}
