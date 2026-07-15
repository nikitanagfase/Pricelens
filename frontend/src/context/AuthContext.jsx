/**
 * context/AuthContext.jsx
 * ─────────────────────────────────────────────
 * Tiny global auth state: who's logged in, plus
 * login()/signup()/logout() actions. The JWT is
 * persisted to localStorage so refreshing the page
 * doesn't log you out (this is a real standalone app
 * running in the user's own browser, not a sandboxed
 * Claude artifact — localStorage is the correct tool here).
 */
import { createContext, useContext, useState, useCallback } from "react";
import * as api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("pricelens_user");
    return raw ? JSON.parse(raw) : null;
  });

  const persist = (token, userObj) => {
    localStorage.setItem("pricelens_token", token);
    localStorage.setItem("pricelens_user", JSON.stringify(userObj));
    setUser(userObj);
  };

  const doLogin = useCallback(async (email, password) => {
    const data = await api.login(email, password);
    persist(data.access_token, data.user);
    return data.user;
  }, []);

  const doSignup = useCallback(async (fullName, email, password) => {
    const data = await api.signup(fullName, email, password);
    persist(data.access_token, data.user);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("pricelens_token");
    localStorage.removeItem("pricelens_user");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login: doLogin, signup: doSignup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
