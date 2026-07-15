/**
 * services/api.js
 * ─────────────────────────────────────────────
 * Every backend call lives here. Components never
 * call axios/fetch directly — they import from this
 * file. One source of truth for endpoint shapes.
 */
import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "";
// '' (empty) lets Vite's dev-server proxy handle '/api/...' calls
// during `npm run dev`. In production, set VITE_API_URL to your
// deployed FastAPI URL (see .env.example).

const api = axios.create({ baseURL });

// Attach JWT (if present) to every request automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("pricelens_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Auth ──────────────────────────────────────────────
export const signup = (full_name, email, password) =>
  api.post("/api/auth/signup", { full_name, email, password }).then((r) => r.data);

export const login = (email, password) =>
  api.post("/api/auth/login", { email, password }).then((r) => r.data);

// ── Flights ───────────────────────────────────────────
export const searchFlights = (payload) =>
  api.post("/api/flights/search", payload).then((r) => r.data);

// ── Prediction ────────────────────────────────────────
export const predictPrice = (payload) =>
  api.post("/api/predict", payload).then((r) => r.data);

// ── Analytics ─────────────────────────────────────────
export const getPriceHistory = (origin, destination, period) =>
  api.get("/api/analytics/history", { params: { origin, destination, period } }).then((r) => r.data);

export const getDayOfWeek = (origin, destination) =>
  api.get("/api/analytics/day-of-week", { params: { origin, destination } }).then((r) => r.data);

export const getAirlineComparison = (origin, destination) =>
  api.get("/api/analytics/airlines", { params: { origin, destination } }).then((r) => r.data);

export const getFestivals = () =>
  api.get("/api/analytics/festivals").then((r) => r.data);

export const getRouteStats = (origin, destination) =>
  api.get("/api/analytics/route-stats", { params: { origin, destination } }).then((r) => r.data);

export const getHeatmap = (origin, destination) =>
  api.get("/api/analytics/heatmap", { params: { origin, destination } }).then((r) => r.data);

// ── Budget Planner ────────────────────────────────────
export const planBudget = (payload) =>
  api.post("/api/budget/plan", payload).then((r) => r.data);

// ── Smart Fare Alerts ─────────────────────────────────
export const listAlerts = () => api.get("/api/alerts").then((r) => r.data);
export const createAlert = (payload) => api.post("/api/alerts", payload).then((r) => r.data);
export const deleteAlert = (id) => api.delete(`/api/alerts/${id}`).then((r) => r.data);

// ── AI Chat (bonus) ───────────────────────────────────
export const sendChatMessage = (message) =>
  api.post("/api/chat", { message }).then((r) => r.data);

export default api;
