import axios from "axios";

/**
 * Shared axios instance. Attaches the admin JWT (if present) to every
 * request, and clears it + redirects to /login on a 401 so an expired
 * session doesn't silently fail admin actions.
 */
const api = axios.create({ baseURL: "/" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && localStorage.getItem("admin_token")) {
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_profile");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
