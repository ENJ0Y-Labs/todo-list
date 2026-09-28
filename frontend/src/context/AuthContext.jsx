import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    let mounted = true;

    api.me()
      .then((data) => {
        if (mounted) setUser(data?.user || null);
      })
      .catch(() => {
        if (mounted) setUser(null);
      })
      .finally(() => {
        if (mounted) setCheckingAuth(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const value = useMemo(() => ({
    user,
    checkingAuth,
    setUser,
    async login(payload) {
      const data = await api.login(payload);
      setUser(data.user);
      return data;
    },
    async register(payload) {
      const data = await api.register(payload);
      setUser(data.user);
      return data;
    },
    async logout() {
      await api.logout();
      setUser(null);
    },
  }), [user, checkingAuth]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
