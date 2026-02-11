import { createContext, useContext, useEffect, useMemo, useState } from "react";

import api from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("ai_pr_token"));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("ai_pr_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const validateSession = async () => {
      const existingToken = localStorage.getItem("ai_pr_token");
      if (!existingToken) {
        setLoading(false);
        return;
      }

      try {
        const { data } = await api.get("/auth/me");
        setUser(data);
        localStorage.setItem("ai_pr_user", JSON.stringify(data));
      } catch (_error) {
        localStorage.removeItem("ai_pr_token");
        localStorage.removeItem("ai_pr_user");
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    validateSession();
  }, []);

  const login = (nextToken, nextUser) => {
    localStorage.setItem("ai_pr_token", nextToken);
    localStorage.setItem("ai_pr_user", JSON.stringify(nextUser));
    setToken(nextToken);
    setUser(nextUser);
  };

  const logout = () => {
    localStorage.removeItem("ai_pr_token");
    localStorage.removeItem("ai_pr_user");
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    const { data } = await api.get("/auth/me");
    setUser(data);
    localStorage.setItem("ai_pr_user", JSON.stringify(data));
    return data;
  };

  const value = useMemo(
    () => ({ token, user, loading, isAuthenticated: Boolean(token), login, logout, refreshUser }),
    [token, user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
