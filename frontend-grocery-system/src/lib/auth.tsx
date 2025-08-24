import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { AuthAPI } from "./api";
import type { ApiUser } from "../interfaces";

type User = ApiUser;

type AuthContextType = {
  user: User | null;
  accessToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const userStr = localStorage.getItem("user");
    if (token && userStr) {
      setAccessToken(token);
      try {
        setUser(JSON.parse(userStr));
      } catch {}
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const data = await AuthAPI.login({ email, password });
    setUser(data.user);
    setAccessToken(data.tokens.access);
    localStorage.setItem("access_token", data.tokens.access);
    localStorage.setItem("refresh_token", data.tokens.refresh);
    localStorage.setItem("user", JSON.stringify(data.user));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setAccessToken(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  }, []);

  const value = useMemo<AuthContextType>(() => ({ user, accessToken, login, logout }), [user, accessToken, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}


