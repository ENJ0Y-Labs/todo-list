const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

async function request(path, options = {}) {
  const response = await fetch(API_BASE_URL + path, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (response.status === 204) return null;

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    const error = new Error(body?.error?.message || "Request failed.");
    error.code = body?.error?.code;
    error.status = response.status;
    throw error;
  }

  return body;
}

export const api = {
  register: (payload) => request("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  }),

  login: (payload) => request("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  }),

  logout: () => request("/auth/logout", { method: "POST" }),

  me: () => request("/auth/me"),

  listTasks: (query = "") => request("/tasks" + (query ? "?" + query : "")),

  createTask: (payload) => request("/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  }),

  getTask: (id) => request("/tasks/" + id),

  updateTask: (id, payload) => request("/tasks/" + id, {
    method: "PATCH",
    body: JSON.stringify(payload),
  }),

  deleteTask: (id) => request("/tasks/" + id, {
    method: "DELETE",
  }),

  setTaskCompleted: (id, completed) => request("/tasks/" + id + "/complete", {
    method: "PATCH",
    body: JSON.stringify({ completed }),
  }),
};
