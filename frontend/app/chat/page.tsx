"use client";
import { useState, useEffect, useRef, useCallback, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { api } from "@/lib/api";
import UserMenu from "@/app/components/UserMenu";
import ChatSidebar, { type Conversation } from "@/app/components/ChatSidebar";

type Message = {
  role: "user" | "assistant";
  content: string;
  pending?: boolean;
};

const QUICK_ACTIONS = [
  "🔥 Aquecimento para treino de ritmo",
  "⚡ O que comer antes do longão?",
  "🏃 Dicas para melhorar meu pace",
  "📋 Me ajuda a montar meu treino de hoje",
  "🩺 Estou sentindo dor no joelho, e agora?",
];

// Simples renderizador de markdown
function renderMarkdown(text: string): ReactNode {
  const lines = text.split("\n");
  const result: ReactNode[] = [];
  let listItems: string[] = [];
  let listType: "bullet" | "numbered" | null = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Flush pending list
    if (
      listItems.length > 0 &&
      !trimmed.match(/^[-*]\s/) &&
      !trimmed.match(/^\d+\.\s/)
    ) {
      if (listType === "bullet") {
        result.push(
          <ul key={`list-${i}`} className="list-disc list-inside space-y-1 my-2">
            {listItems.map((item, idx) => (
              <li key={idx} className="text-zinc-100">
                {renderInlineMarkdown(item)}
              </li>
            ))}
          </ul>
        );
      } else if (listType === "numbered") {
        result.push(
          <ol key={`list-${i}`} className="list-decimal list-inside space-y-1 my-2">
            {listItems.map((item, idx) => (
              <li key={idx} className="text-zinc-100">
                {renderInlineMarkdown(item)}
              </li>
            ))}
          </ol>
        );
      }
      listItems = [];
      listType = null;
    }

    // Headings
    if (trimmed.startsWith("## ")) {
      result.push(
        <h2 key={i} className="text-white font-semibold text-sm mt-3 mb-1">
          {renderInlineMarkdown(trimmed.slice(3))}
        </h2>
      );
    } else if (trimmed.startsWith("### ")) {
      result.push(
        <h3 key={i} className="text-white font-semibold text-sm mt-3 mb-1">
          {renderInlineMarkdown(trimmed.slice(4))}
        </h3>
      );
    }
    // List items
    else if (trimmed.match(/^[-*]\s/)) {
      const item = trimmed.slice(2);
      if (listType !== "bullet") {
        if (listItems.length > 0) {
          if (listType === "numbered") {
            result.push(
              <ol key={`list-${i}`} className="list-decimal list-inside space-y-1 my-2">
                {listItems.map((li, idx) => (
                  <li key={idx} className="text-zinc-100">
                    {renderInlineMarkdown(li)}
                  </li>
                ))}
              </ol>
            );
          }
          listItems = [];
        }
        listType = "bullet";
      }
      listItems.push(item);
    } else if (trimmed.match(/^\d+\.\s/)) {
      const item = trimmed.replace(/^\d+\.\s/, "");
      if (listType !== "numbered") {
        if (listItems.length > 0) {
          if (listType === "bullet") {
            result.push(
              <ul key={`list-${i}`} className="list-disc list-inside space-y-1 my-2">
                {listItems.map((li, idx) => (
                  <li key={idx} className="text-zinc-100">
                    {renderInlineMarkdown(li)}
                  </li>
                ))}
              </ul>
            );
          }
          listItems = [];
        }
        listType = "numbered";
      }
      listItems.push(item);
    }
    // Empty line
    else if (trimmed === "") {
      result.push(<div key={i} className="h-2" />);
    }
    // Regular paragraph
    else {
      result.push(
        <p key={i} className="text-zinc-100 leading-relaxed">
          {renderInlineMarkdown(trimmed)}
        </p>
      );
    }
  }

  // Flush remaining list
  if (listItems.length > 0) {
    if (listType === "bullet") {
      result.push(
        <ul key="final-list" className="list-disc list-inside space-y-1 my-2">
          {listItems.map((item, idx) => (
            <li key={idx} className="text-zinc-100">
              {renderInlineMarkdown(item)}
            </li>
          ))}
        </ul>
      );
    } else if (listType === "numbered") {
      result.push(
        <ol key="final-list" className="list-decimal list-inside space-y-1 my-2">
          {listItems.map((item, idx) => (
            <li key={idx} className="text-zinc-100">
              {renderInlineMarkdown(item)}
            </li>
          ))}
        </ol>
      );
    }
  }

  return result;
}

// Renderiza inline markdown (bold, italic, code)
function renderInlineMarkdown(text: string): ReactNode {
  const parts: ReactNode[] = [];
  let lastIndex = 0;

  // Regex para capturar **bold**, *italic*, e `code`
  // bold: .+? (não-guloso, permite asteriscos internos)
  // italic: lookahead/lookbehind evita capturar ** como italic
  const regex = /\*\*(.+?)\*\*|\*(?!\*)(.+?)(?<!\*)\*(?!\*)|`([^`]+)`/g;
  let match;

  while ((match = regex.exec(text)) !== null) {
    // Texto antes do match
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    if (match[1]) {
      // **bold**
      parts.push(
        <strong key={match.index} className="font-semibold text-violet-300">
          {match[1]}
        </strong>
      );
    } else if (match[2]) {
      // *italic*
      parts.push(
        <em key={match.index} className="italic text-violet-300">
          {match[2]}
        </em>
      );
    } else if (match[3]) {
      // `code`
      parts.push(
        <code
          key={match.index}
          className="bg-zinc-800 text-violet-300 px-1.5 py-0.5 rounded text-xs font-mono"
        >
          {match[3]}
        </code>
      );
    }

    lastIndex = regex.lastIndex;
  }

  // Texto restante
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length === 0 ? text : parts;
}

export default function ChatPage() {
  const router = useRouter();
  const supabase = createClient();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [profileLoaded, setProfileLoaded] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [userProfile, setUserProfile] = useState<{ name: string; email: string } | null>(null);
  const conversationIdRef = useRef<number | undefined>(undefined);
  const sendingRef = useRef(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // Verificar autenticação via Supabase
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) {
        router.push("/login");
        return;
      }

      // Obter nome do usuário do perfil backend
      api
        .getProfile()
        .then((p: unknown) => {
          const prof = p as { name: string };
          setUserProfile({ name: prof.name, email: user.email || "" });
          setProfileLoaded(true);
          setMessages([
            {
              role: "assistant",
              content: `Oi, ${prof.name}! 💪 Sou o GoJohnny — seu treinador digital de corrida.\n\nEstou aqui pra te ajudar a treinar com mais inteligência, consistência e resultado. Me conta: **o que você precisa hoje?**`,
            },
          ]);
        })
        .catch(() => {
          // Perfil não existe — onboarding conversacional no chat
          setUserProfile({ name: "", email: user.email || "" });
          setProfileLoaded(true);
          setMessages([
            {
              role: "assistant",
              content: "Olá! Sou o GoJohnny, seu treinador de corrida. Antes de começarmos — há quanto tempo você corre?",
            },
          ]);
        });

      // Carregar histórico de conversas
      api
        .getConversations()
        .then((convs: unknown) => {
          const typed = convs as { id: number; title: string; created_at?: string }[];
          setConversations(typed);
        })
        .catch(() => {
          // Ignorar erro ao carregar conversas
        });
    });
  }, [router, supabase.auth]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadConversation = useCallback((id: number) => {
    // Implementação futura: carregar mensagens de uma conversa anterior
    conversationIdRef.current = id;
    // api.getMessages(id).then(setMessages);
    setSidebarOpen(false);
  }, []);

  const startNewChat = useCallback(() => {
    conversationIdRef.current = undefined;
    setMessages([
      {
        role: "assistant",
        content: userProfile?.name
          ? `Oi, ${userProfile.name}! 💪 Sou o GoJohnny — seu treinador digital de corrida.\n\nEstou aqui pra te ajudar a treinar com mais inteligência, consistência e resultado. Me conta: **o que você precisa hoje?**`
          : "Olá! Sou o GoJohnny, seu treinador de corrida. Antes de começarmos — há quanto tempo você corre?",
      },
    ]);
    setSidebarOpen(false);
  }, [userProfile?.name]);

  const send = useCallback(async (text: string) => {
    if (!text.trim() || sendingRef.current) return;

    // Remove emoji do início da ação rápida
    const cleanText = text.replace(/^[\p{Emoji}\s]+/u, "").trim();

    if (!cleanText) return;

    sendingRef.current = true;
    setInput("");
    setMessages((m) => [
      ...m,
      { role: "user", content: cleanText },
      { role: "assistant", content: "", pending: true },
    ]);
    setLoading(true);

    try {
      const data = await api.sendMessage(cleanText, conversationIdRef.current);
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

  // Quick actions aparecem apenas quando o perfil carregou e só há a mensagem de boas-vindas
  const showQuickActions = profileLoaded && messages.length === 1;

  return (
    <div className="flex h-screen bg-zinc-950">
      {/* Sidebar */}
      <ChatSidebar
        conversations={conversations}
        currentId={conversationIdRef.current}
        onSelect={loadConversation}
        onNewChat={startNewChat}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Área principal */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/50">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-zinc-800 transition-colors sm:hidden"
              aria-label="Toggle sidebar"
            >
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm"
              style={{
                background: "linear-gradient(135deg, #7c3aed, #a855f7)",
              }}
            >
              G
            </div>
            <div>
              <p className="text-white font-semibold text-sm leading-none">
                GoJohnny
              </p>
              <p className="text-violet-400 text-xs">
                ● Treinador ativo
              </p>
            </div>
          </div>
          {userProfile && (
            <UserMenu name={userProfile.name} email={userProfile.email} />
          )}
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"} animate-slide-up`}
            >
              {m.role === "assistant" && (
                <div
                  className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold mr-2 flex-shrink-0 mt-0.5"
                  style={{
                    background: "linear-gradient(135deg, #7c3aed, #a855f7)",
                    boxShadow: "0 0 12px rgba(124, 58, 237, 0.4)",
                  }}
                >
                  G
                </div>
              )}
              <div
                className={`max-w-xs sm:max-w-sm md:max-w-md rounded-lg px-4 py-3 text-sm leading-relaxed ${
                  m.role === "user"
                    ? "rounded-br-none text-white"
                    : "border border-zinc-700 rounded-tl-none text-zinc-100"
                }`}
                style={
                  m.role === "user"
                    ? {
                        background: "linear-gradient(135deg, #7c3aed, #6d28d9)",
                      }
                    : {
                        background: "#18181b",
                        borderLeftColor: "#7c3aed",
                        borderLeftWidth: "2px",
                      }
                }
              >
                {m.pending ? (
                  <span className="flex gap-1 items-center h-5">
                    <span className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-typing-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-typing-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-typing-bounce" style={{ animationDelay: "300ms" }} />
                    <span className="text-xs text-zinc-500 ml-1">pensando...</span>
                  </span>
                ) : m.role === "user" ? (
                  m.content
                ) : (
                  renderMarkdown(m.content)
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
                className="text-xs px-3 py-1.5 rounded-full border transition-all disabled:opacity-50 text-zinc-300 hover:text-violet-300 border-zinc-700 hover:border-violet-500"
                style={{
                  background: "rgba(124, 58, 237, 0.08)",
                }}
              >
                {a}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="px-4 pb-4 pt-2 border-t border-zinc-800">
          <div
            className="flex gap-2 border rounded-2xl px-4 py-2 transition-colors focus-within:border-violet-500"
            style={{
              background: "#111116",
              borderColor: "#27272a",
            }}
          >
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              disabled={loading}
              placeholder="Fale com seu treinador... (Enter para enviar)"
              className="flex-1 bg-transparent text-white text-sm resize-none outline-none placeholder-zinc-600 max-h-32 py-1"
              style={{ scrollbarWidth: "none" }}
            />
            <button
              onClick={() => send(input)}
              disabled={!input.trim() || loading}
              aria-label="Enviar mensagem"
              className="self-end w-8 h-8 rounded-lg disabled:opacity-30 flex items-center justify-center transition-all flex-shrink-0 text-white"
              style={{
                background: "linear-gradient(135deg, #7c3aed, #a855f7)",
              }}
            >
              <svg
                className="w-4 h-4"
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
            GoJohnny é um treinador digital — sempre consulte um profissional de saúde para questões médicas.
          </p>
        </div>
      </div>
    </div>
  );
}
