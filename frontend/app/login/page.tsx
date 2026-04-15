"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [tab, setTab] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    // BUG-01: autenticação e verificação de perfil em blocos separados.
    // Erros de rede no getProfile não devem exibir mensagem de autenticação.
    let authenticated = false;
    try {
      const fn = tab === "login" ? api.login : api.register;
      const data = await fn(email, password);
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      // Cookie leve usado pelo middleware (Edge Runtime não acessa localStorage)
      document.cookie = "has_session=1; path=/; SameSite=Lax";
      authenticated = true;
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao autenticar");
      setLoading(false);
      return;
    }

    if (authenticated) {
      // Verificação de perfil: qualquer falha (inclusive erro de rede) redireciona
      // para /onboarding — nunca exibe mensagem de erro de autenticação.
      try {
        await api.getProfile();
        router.push("/chat");
      } catch {
        router.push("/onboarding");
      }
      // Não chama setLoading(false) aqui: o redirect vai desmontar o componente.
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-zinc-950 px-4"
      style={{
        background:
          "linear-gradient(135deg, #09090b 0%, #0f0b1a 100%)",
      }}
    >
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          {/* G Icon with gradient */}
          <div className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center font-bold text-lg text-white flex-shrink-0"
            style={{
              background: "linear-gradient(135deg, #7c3aed, #a855f7)",
            }}
          >
            G
          </div>
          <h1 className="text-4xl font-bold text-white"
            style={{
              background: "linear-gradient(to right, #a78bfa, #a855f7)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            GoJohnny
          </h1>
          <p className="text-zinc-400 mt-2 text-sm">Seu treinador digital de corrida</p>
        </div>

        {/* Card */}
        <div
          className="bg-zinc-900/50 rounded-3xl p-8 border border-zinc-800"
          style={{
            boxShadow: "0 0 40px rgba(124, 58, 237, 0.08)",
          }}
        >
          {/* Tabs */}
          <div className="flex rounded-xl bg-zinc-800 p-1 mb-6">
            {(["login", "register"] as const).map((t) => (
              <button
                key={t}
                onClick={() => {
                  setTab(t);
                  setError("");
                }}
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  tab === t
                    ? "text-white"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
                style={
                  tab === t
                    ? {
                        background: "linear-gradient(135deg, #7c3aed, #6d28d9)",
                      }
                    : {}
                }
              >
                {t === "login" ? "Entrar" : "Criar conta"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-zinc-400 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-zinc-800/50 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all"
                placeholder="voce@email.com"
              />
            </div>
            <div>
              <label className="block text-sm text-zinc-400 mb-2">Senha</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full bg-zinc-800/50 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <p className="text-red-400 text-sm bg-red-950/30 border border-red-800/50 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full text-white font-semibold py-3 rounded-lg transition-all disabled:opacity-50 mt-2"
              style={{
                background: loading
                  ? "linear-gradient(135deg, #7c3aed, #6d28d9)"
                  : "linear-gradient(135deg, #7c3aed, #a855f7)",
              }}
            >
              {loading ? "Aguarde..." : tab === "login" ? "Entrar" : "Criar conta"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
