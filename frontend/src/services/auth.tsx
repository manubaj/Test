import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api } from "./api";
import type { UserRole } from "../types/api";

interface AuthState {
  token: string | null;
  username: string | null;
  role: UserRole | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("access_token")
  );
  const [username, setUsername] = useState<string | null>(
    localStorage.getItem("username")
  );
  const [role, setRole] = useState<UserRole | null>(
    (localStorage.getItem("role") as UserRole | null) || null
  );

  const value = useMemo<AuthState>(
    () => ({
      token,
      username,
      role,
      async login(email, password) {
        const res = await api.login(email, password);
        localStorage.setItem("access_token", res.access_token);
        localStorage.setItem("username", res.username);
        localStorage.setItem("role", res.role);
        setToken(res.access_token);
        setUsername(res.username);
        setRole(res.role);
      },
      logout() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("username");
        localStorage.removeItem("role");
        setToken(null);
        setUsername(null);
        setRole(null);
      },
    }),
    [token, username, role]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
