import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(() => {
    const stored = localStorage.getItem("admin_profile");
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get("/api/auth/me")
      .then((res) => {
        setAdmin(res.data);
        localStorage.setItem("admin_profile", JSON.stringify(res.data));
      })
      .catch(() => {
        localStorage.removeItem("admin_token");
        localStorage.removeItem("admin_profile");
        setAdmin(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    const res = await api.post("/api/auth/login", { email, password });
    localStorage.setItem("admin_token", res.data.access_token);
    localStorage.setItem("admin_profile", JSON.stringify(res.data.admin));
    setAdmin(res.data.admin);
    return res.data.admin;
  }

  function logout() {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_profile");
    setAdmin(null);
  }

  function updateAdminProfile(updated) {
    setAdmin(updated);
    localStorage.setItem("admin_profile", JSON.stringify(updated));
  }

  return (
    <AuthContext.Provider value={{ admin, loading, login, logout, updateAdminProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
