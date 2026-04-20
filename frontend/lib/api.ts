import { createClient } from "./supabase";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8011";

// Timeout padrão para requisições ao backend (ms)
const DEFAULT_TIMEOUT_MS = 10_000;

async function authHeaders(): Promise<Record<string, string>> {
  if (typeof window === "undefined") {
    return {};
  }

  try {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.refreshSession();
    const token = session?.access_token;
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
}

async function req<T>(
  path: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS
): Promise<T> {
  const headers = await authHeaders();

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(`${BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...headers,
        ...(options.headers as Record<string, string>),
      },
      signal: controller.signal,
      ...options,
    });

    // 401: sessão expirou — redirecionar para login via Supabase (signOut)
    if (res.status === 401) {
      if (typeof window !== "undefined") {
        try {
          const supabase = createClient();
          await supabase.auth.signOut();
        } catch {
          // Ignorar erro ao fazer sign out
        }
        window.location.href = "/login";
      }
      throw new Error("Sessão expirada. Faça login novamente.");
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Erro desconhecido");
    }

    if (res.status === 204) return undefined as T;
    return res.json();
  } finally {
    clearTimeout(timeoutId);
  }
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

  // Profile — timeout reduzido: falha rápida, onboarding no chat assume o controle
  getProfile: () => req("/profile", {}, 5_000),
  createProfile: (data: object) =>
    req("/profile", { method: "POST", body: JSON.stringify(data) }),
  updateProfile: (data: object) =>
    req("/profile", { method: "PUT", body: JSON.stringify(data) }),

  // Chat — timeout maior para respostas da IA
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
    }, 30_000),

  getConversations: () => req<{ id: number; title: string }[]>("/chat/conversations"),
  getMessages: (id: number) => req<{ role: string; content: string; created_at: string }[]>(
    `/chat/conversations/${id}/messages`
  ),

  // Plans
  generatePlan: () => req("/plans/generate", { method: "POST" }, 30_000),
  getCurrentPlan: () => req("/plans/current"),

  // Feedback
  submitFeedback: (data: object) =>
    req("/feedback", { method: "POST", body: JSON.stringify(data) }),
  getFeedbacks: () => req("/feedback"),
};
