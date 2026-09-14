import axios from "axios";

// Base URL for the FastAPI backend. In dev this defaults to the local
// uvicorn server; in production it's injected at build time via Vite env.
const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ||
  "http://localhost:8000";

export const CURRENT_USER_STORAGE_KEY = "docs-app:current-user-id";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Every authenticated request carries the mocked identity as an
// X-User-Id header, per the backend's mocked-auth contract
// (backend/src/api/deps.py). We read it fresh from localStorage on every
// request rather than caching it in a closure, so switching the "logged
// in as" user takes effect immediately without re-creating the client.
apiClient.interceptors.request.use((config) => {
  const userId = localStorage.getItem(CURRENT_USER_STORAGE_KEY);
  if (userId) {
    config.headers.set("X-User-Id", userId);
  }
  return config;
});

export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (error.message) return error.message;
  }
  if (error instanceof Error) return error.message;
  return "Something went wrong.";
}
