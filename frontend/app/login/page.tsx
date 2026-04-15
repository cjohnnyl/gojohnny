"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const supabase = createClient();
  const [tab, setTab] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [confirmationSent, setConfirmationSent] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (tab === "login") {
      // Login com Supabase
      try {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (signInError) {
          setError(signInError.message || "Erro ao fazer login");
          setLoading(false);
          return;
        }

        // Verificar perfil — se não tiver, bot fará onboarding no chat
        try {
          await api.getProfile();
          router.push("/chat");
        } catch {
          // Perfil não existe — o chat fará onboarding conversacional
          router.push("/chat");
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Erro ao fazer login");
        setLoading(false);
      }
    } else {
      // Registro com Supabase
      try {
        const { error: signUpError } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${window.location.origin}/auth/callback`,
          },
        });

        if (signUpError) {
          setError(signUpError.message || "Erro ao criar conta");
          setLoading(false);
          return;
        }

        setConfirmationSent(true);
        setLoading(false);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Erro ao criar conta");
        setLoading(false);
      }
    }
  }

  async function handleForgotPassword(e: React.FormEvent) {
    e.preventDefault();
    if (!email) {
      setError("Digite seu email");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      });

      if (error) {
        setError(error.message || "Erro ao enviar email de recuperação");
        setLoading(false);
        return;
      }

      setError("");
      alert(
        "Email de recuperação enviado! Verifique sua caixa de entrada."
      );
      setLoading(false);
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "Erro ao enviar email"
      );
      setLoading(false);
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

          {confirmationSent ? (
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-violet-500/20 border border-violet-500/30">
                <svg
                  className="w-6 h-6 text-violet-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <p className="text-white font-medium">Conta criada com sucesso!</p>
              <p className="text-zinc-400 text-sm">
                Verifique seu email para ativar sua conta. Um link de confirmação foi enviado para{" "}
                <span className="text-white">{email}</span>.
              </p>
              <button
                onClick={() => {
                  setConfirmationSent(false);
                  setEmail("");
                  setPassword("");
                }}
                className="text-sm text-violet-400 hover:text-violet-300 transition"
              >
                Voltar para login
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                  className="w-full bg-zinc-800/50 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all disabled:opacity-50"
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
                  disabled={loading}
                  className="w-full bg-zinc-800/50 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all disabled:opacity-50"
                  placeholder="••••••••"
                />
              </div>

              {error && (
                <p className="text-red-400 text-sm bg-red-950/30 border border-red-800/50 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              {tab === "login" && (
                <div className="text-right">
                  <button
                    type="button"
                    onClick={handleForgotPassword}
                    disabled={loading || !email}
                    className="text-xs text-violet-400 hover:text-violet-300 transition disabled:opacity-50"
                  >
                    Esqueci minha senha
                  </button>
                </div>
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
          )}
        </div>
      </div>
    </div>
  );
}
