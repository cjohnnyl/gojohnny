const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8011";

function authHeaders(token?: string | null): Record<string, string> {
  const t =
    token ??
    (typeof window !== "undefined" ? localStorage.getItem("access_token") : null);
  return t ? { Authorization: `Bearer ${t}` } : {};
}

// BUG-06: tenta renovar o access_token usando o refresh_token armazenado.
// Retorna o novo access_token ou lança erro se o refresh falhar.
async function tryRefresh(): Promise<string> {
  const refreshToken =
    typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;

  if (!refreshToken) throw new Error("Sem refresh token");

  const res = await fetch(`${BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!res.ok) throw new Error("Refresh inválido");

  const data = await res.json() as { access_token: string; refresh_token: string };
  // Persiste o novo refresh_token — o backend emite um par novo a cada refresh
  if (data.refresh_token && typeof window !== "undefined") {
    localStorage.setItem("refresh_token", data.refresh_token);
  }
  return data.access_token;
}

async function req<T>(
  path: string,
  options: RequestInit = {},
  isRetry = false
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers as Record<string, string>),
    },
    ...options,
  });

  // BUG-06: ao receber 401, tenta refresh uma única vez antes de desistir.
  if (res.status === 401 && !isRetry) {
    try {
      const newToken = await tryRefresh();
      localStorage.setItem("access_token", newToken);

      // Repete a requisição original com o novo token.
      const retryRes = await fetch(`${BASE}${path}`, {
        headers: {
          "Content-Type": "application/json",
          ...authHeaders(newToken),
          ...(options.headers as Record<string, string>),
        },
        ...options,
      });

      if (!retryRes.ok) {
        const err = await retryRes.json().catch(() => ({ detail: retryRes.statusText }));
        throw new Error(err.detail || "Erro desconhecido");
      }

      if (retryRes.status === 204) return undefined as T;
      return retryRes.json();
    } catch {
      // Refresh falhou: limpa sessão e redireciona para login.
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      }
      throw new Error("Sessão expirada. Faça login novamente.");
    }
  }

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
