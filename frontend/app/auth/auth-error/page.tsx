"use client";
import { useRouter } from "next/navigation";

export default function AuthErrorPage() {
  const router = useRouter();

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
          <p className="text-zinc-400 mt-2 text-sm">Erro de autenticação</p>
        </div>

        {/* Card */}
        <div
          className="bg-zinc-900/50 rounded-3xl p-8 border border-zinc-800"
          style={{
            boxShadow: "0 0 40px rgba(124, 58, 237, 0.08)",
          }}
        >
          <div className="text-center space-y-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-500/20 border border-red-500/30">
              <svg
                className="w-6 h-6 text-red-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
            <p className="text-white font-medium">Erro ao processar autenticação</p>
            <p className="text-zinc-400 text-sm">
              O link de autenticação pode ter expirado ou ser inválido.
            </p>
            <button
              onClick={() => router.push("/login")}
              className="w-full text-white font-semibold py-3 rounded-lg transition-all mt-4"
              style={{
                background: "linear-gradient(135deg, #7c3aed, #a855f7)",
              }}
            >
              Voltar para login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
