const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function authHeaders(): Record<string, string> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function req<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers as Record<string, string>),
    },
    ...options,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erro desconhecido");
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// Auth
export const api = {
  register: (email: string, password: string) =>
    req<{ access_token: string; refresh_token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    req<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  // Profile
  getProfile: () => req("/profile"),
  createProfile: (data: object) =>
    req("/profile", { method: "POST", body: JSON.stringify(data) }),
  updateProfile: (data: object) =>
    req("/profile", { method: "PUT", body: JSON.stringify(data) }),

  // Chat
  sendMessage: (content: string, conversation_id?: number) =>
    req<{
      conversation_id: number;
      message_id: number;
      role: string;
      content: string;
      tokens_used: number;
    }>("/chat/message", {
      method: "POST",
      body: JSON.stringify({ content, conversation_id }),
    }),

  getConversations: () => req<{ id: number; title: string }[]>("/chat/conversations"),
  getMessages: (id: number) => req<{ role: string; content: string; created_at: string }[]>(
    `/chat/conversations/${id}/messages`
  ),

  // Plans
  generatePlan: () => req("/plans/generate", { method: "POST" }),
  getCurrentPlan: () => req("/plans/current"),

  // Feedback
  submitFeedback: (data: object) =>
    req("/feedback", { method: "POST", body: JSON.stringify(data) }),
  getFeedbacks: () => req("/feedback"),
};
