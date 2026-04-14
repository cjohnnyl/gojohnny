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
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">GoJohnny</h1>
          <p className="text-zinc-400 mt-1 text-sm">Seu treinador digital de corrida de rua</p>
        </div>

        {/* Card */}
        <div className="bg-zinc-900 rounded-2xl p-8 border border-zinc-800">
          {/* Tabs */}
          <div className="flex rounded-lg bg-zinc-800 p-1 mb-6">
            {(["login", "register"] as const).map((t) => (
              <button
                key={t}
                onClick={() => { setTab(t); setError(""); }}
                className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${
                  tab === t
                    ? "bg-zinc-600 text-white"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                {t === "login" ? "Entrar" : "Criar conta"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-zinc-400 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="voce@email.com"
              />
            </div>
            <div>
              <label className="block text-sm text-zinc-400 mb-1">Senha</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
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
              className="w-full bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white font-semibold py-2.5 rounded-lg transition-colors"
            >
              {loading ? "Aguarde..." : tab === "login" ? "Entrar" : "Criar conta"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
