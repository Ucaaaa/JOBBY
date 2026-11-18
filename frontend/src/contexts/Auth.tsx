import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api } from "../api";

type User = { id: number; name: string; email: string };
type Ctx = { setUser: (u: User) => void; user: User | null; loading: boolean; login: (e: string, p: string) => Promise<void>;
  register: (n: string, e: string, p: string) => Promise<void>; logout: () => void };
const AuthCtx = createContext<Ctx>(null as unknown as Ctx);
export const useAuth = () => useContext(AuthCtx);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(!!localStorage.getItem("jobby_token"));
  useEffect(() => {
    if (!localStorage.getItem("jobby_token")) return;
    api("/auth/me").then((d) => setUser(d.user)).catch(() => localStorage.removeItem("jobby_token")).finally(() => setLoading(false));
  }, []);
  const done = (d: { token: string; user: User }) => { localStorage.setItem("jobby_token", d.token); setUser(d.user); };
  return (
    <AuthCtx.Provider value={{ user, loading, setUser,
      login: async (email, password) => done(await api("/auth/login", { method: "POST", body: { email, password } })),
      register: async (name, email, password) => done(await api("/auth/register", { method: "POST", body: { name, email, password } })),
      logout: () => { localStorage.removeItem("jobby_token"); setUser(null); } }}>
      {children}
    </AuthCtx.Provider>
  );
}
