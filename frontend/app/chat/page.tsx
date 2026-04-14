"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
  pending?: boolean;
};

const QUICK_ACTIONS = [
  "Gera minha planilha da semana",
  "Como foi meu último treino?",
  "Qual o melhor aquecimento antes de um treino de ritmo?",
  "O que comer antes de um longão?",
  "Dicas para melhorar meu pace",
];

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [profileLoaded, setProfileLoaded] = useState(false);
  const conversationIdRef = useRef<number | undefined>(undefined);
  const sendingRef = useRef(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    api
      .getProfile()
      .then((p: unknown) => {
        const prof = p as { name: string };
        setProfileLoaded(true);
        setMessages([
          {
            role: "assistant",
            content: `Olá, ${prof.name}! Sou o GoJohnny, seu treinador digital de corrida. Como posso te ajudar hoje?`,
          },
        ]);
      })
      .catch(() => router.push("/onboarding"));
  }, [router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = useCallback(async (text: string) => {
    if (!text.trim() || sendingRef.current) return;

    const content = text.trim();
    sendingRef.current = true;
    setInput("");
    setMessages((m) => [
      ...m,
      { role: "user", content },
      { role: "assistant", content: "", pending: true },
    ]);
    setLoading(true);

    try {
      const data = await api.sendMessage(content, conversationIdRef.current);
      conversationIdRef.current = data.conversation_id;
      setMessages((m) => {
        const updated = [...m];
        updated[updated.length - 1] = {
          role: "assistant",
          content: data.content,
        };
        return updated;
      });
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Erro ao enviar mensagem";
      setMessages((m) => {
        const updated = [...m];
        updated[updated.length - 1] = {
          role: "assistant",
          content: `Erro: ${msg}`,
        };
        return updated;
      });
    } finally {
      sendingRef.current = false;
      setLoading(false);
      inputRef.current?.focus();
    }
  }, []);

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  }

  function logout() {
    localStorage.clear();
    router.push("/login");
  }

  // Quick actions aparecem apenas quando o perfil carregou e só há a mensagem de boas-vindas
  const showQuickActions = profileLoaded && messages.length === 1;

  return (
    <div className="flex flex-col h-screen bg-zinc-950">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center text-white font-bold text-sm">
            G
          </div>
          <div>
            <p className="text-white font-semibold text-sm leading-none">
              GoJohnny
            </p>
            <p className="text-zinc-500 text-xs">
              Treinador digital de corrida
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => router.push("/plano")}
            className="text-zinc-400 hover:text-white text-xs px-3 py-1.5 rounded-lg border border-zinc-700 hover:border-zinc-500 transition-colors"
          >
            Planilha
          </button>
          <button
            onClick={logout}
            className="text-zinc-500 hover:text-zinc-300 text-xs px-3 py-1.5 rounded-lg hover:bg-zinc-800 transition-colors"
          >
            Sair
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {m.role === "assistant" && (
              <div className="w-7 h-7 rounded-full bg-orange-500 flex items-center justify-center text-white text-xs font-bold mr-2 flex-shrink-0 mt-0.5">
                G
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                m.role === "user"
                  ? "bg-orange-500 text-white rounded-tr-sm"
                  : "bg-zinc-800 text-zinc-100 rounded-tl-sm"
              }`}
            >
              {m.pending ? (
                <span className="flex gap-1 items-center h-5">
                  <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce [animation-delay:0ms]" />
                  <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce [animation-delay:150ms]" />
                  <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce [animation-delay:300ms]" />
                </span>
              ) : (
                m.content
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Quick actions — aparece só após o perfil carregar e apenas com a mensagem inicial */}
      {showQuickActions && (
        <div className="px-4 pb-2 flex flex-wrap gap-2 justify-center">
          {QUICK_ACTIONS.map((a) => (
            <button
              key={a}
              onClick={() => send(a)}
              disabled={loading}
              className="text-xs bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 text-zinc-300 px-3 py-1.5 rounded-full border border-zinc-700 transition-colors"
            >
              {a}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="px-4 pb-4 pt-2 border-t border-zinc-800">
        <div className="flex gap-2 bg-zinc-900 border border-zinc-700 rounded-2xl px-4 py-2 focus-within:border-orange-500 transition-colors">
          <textarea
            ref={inputRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            disabled={loading}
            placeholder="Escreva sua mensagem... (Enter para enviar)"
            className="flex-1 bg-transparent text-white text-sm resize-none outline-none placeholder-zinc-500 max-h-32 py-1"
            style={{ scrollbarWidth: "none" }}
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            aria-label="Enviar mensagem"
            className="self-end w-8 h-8 rounded-xl bg-orange-500 hover:bg-orange-600 disabled:opacity-30 flex items-center justify-center transition-colors flex-shrink-0"
          >
            <svg
              className="w-4 h-4 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
        <p className="text-zinc-600 text-xs text-center mt-2">
          GoJohnny não substitui médico, nutricionista ou fisioterapeuta.
        </p>
      </div>
    </div>
  );
}
