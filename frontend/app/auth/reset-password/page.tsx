"use client";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createClient } from "@/lib/supabase";

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  // Verificar se o usuário está autenticado com o token de recuperação
  const supabase = createClient();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    // Validação básica
    if (password.length < 6) {
      setError("A senha deve ter no mínimo 6 caracteres");
      setLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError("As senhas não correspondem");
      setLoading(false);
      return;
    }

    try {
      const { error } = await supabase.auth.updateUser({ password });

      if (error) {
        setError(error.message || "Erro ao redefinir senha");
        setLoading(false);
        return;
      }

      setSuccess(true);
      // Redirecionar para login após 2 segundos
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erro ao redefinir senha"
      );
      setLoading(false);
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-zinc-950 px-4"
      style={{
        background: "linear-gradient(135deg, #09090b 0%, #0f0b1a 100%)",
      }}
    >
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div
            className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center font-bold text-lg text-white flex-shrink-0"
            style={{
              background: "linear-gradient(135deg, #7c3aed, #a855f7)",
            }}
          >
            G
          </div>
          <h1
            className="text-4xl font-bold text-white"
            style={{
              background: "linear-gradient(to right, #a78bfa, #a855f7)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            GoJohnny
          </h1>
          <p className="text-zinc-400 mt-2 text-sm">Redefinir senha</p>
        </div>

        {/* Card */}
        <div
          className="bg-zinc-900/50 rounded-3xl p-8 border border-zinc-800"
          style={{
            boxShadow: "0 0 40px rgba(124, 58, 237, 0.08)",
          }}
        >
          {success ? (
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-500/20 border border-green-500/30">
                <svg
                  className="w-6 h-6 text-green-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <p className="text-white font-medium">Senha redefinida com sucesso!</p>
              <p className="text-zinc-400 text-sm">
                Você será redirecionado para o login em breve...
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  Nova senha
                </label>
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
              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  Confirmar senha
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
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
                {loading ? "Aguarde..." : "Redefinir senha"}
              </button>
            </form>
          )}
        </div>

        <p className="text-zinc-500 text-xs text-center mt-6">
          Ou retorne para{" "}
          <button
            onClick={() => router.push("/login")}
            className="text-violet-400 hover:text-violet-300 transition"
          >
            fazer login
          </button>
        </p>
      </div>
    </div>
  );
}
