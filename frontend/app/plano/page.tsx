"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

type TrainingDay = {
  dia: string;
  tipo: string;
  km: number;
  pace_sugerido: string;
  orientacoes: string;
};

type Plan = {
  id: number;
  week_start: string;
  week_end: string;
  coach_notes: string;
  plan: TrainingDay[];
};

const TYPE_COLORS: Record<string, string> = {
  leve: "bg-green-500/20 text-green-400 border-green-500/30",
  regenerativo: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  ritmo: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  intervalado: "bg-red-500/20 text-red-400 border-red-500/30",
  longao: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  descanso: "bg-zinc-700/50 text-zinc-400 border-zinc-600/30",
};

export default function PlanoPage() {
  const router = useRouter();
  const [plan, setPlan] = useState<Plan | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  const loadPlan = useCallback(async () => {
    try {
      const data = await api.getCurrentPlan();
      setPlan(data as Plan);
    } catch (err: unknown) {
      // 404 significa sem plano — estado vazio esperado
      // outros erros (401 etc.) limpam o estado mas não redirecionam aqui;
      // o middleware de autenticação no api.ts já lança o erro com a mensagem do backend
      const msg = err instanceof Error ? err.message : "";
      if (msg.toLowerCase().includes("not authenticated") || msg.toLowerCase().includes("unauthorized")) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        router.push("/login");
        return;
      }
      setPlan(null);
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    loadPlan();
  }, [router, loadPlan]);

  async function generate() {
    setGenerating(true);
    setError("");
    try {
      const data = await api.generatePlan();
      setPlan(data as Plan);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao gerar planilha");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 pb-10">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900">
        <button onClick={() => router.push("/chat")} className="text-zinc-400 hover:text-white flex items-center gap-1 text-sm transition-colors">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Chat
        </button>
        <h1 className="text-white font-semibold text-sm">Planilha da semana</h1>
        <button
          onClick={generate}
          disabled={generating}
          className="text-orange-400 hover:text-orange-300 text-xs font-medium transition-colors disabled:opacity-50"
        >
          {generating ? "Gerando..." : "Gerar nova"}
        </button>
      </header>

      <div className="max-w-2xl mx-auto px-4 pt-6">
        {loading && (
          <div className="text-center text-zinc-500 py-20">Carregando...</div>
        )}

        {!loading && !plan && !generating && (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-full bg-orange-500/10 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h2 className="text-white font-semibold mb-2">Sem planilha esta semana</h2>
            <p className="text-zinc-400 text-sm mb-6">Gere sua planilha personalizada baseada no seu perfil.</p>
            <button
              onClick={generate}
              className="bg-orange-500 hover:bg-orange-600 text-white font-semibold px-6 py-2.5 rounded-xl transition-colors"
            >
              Gerar planilha
            </button>
          </div>
        )}

        {generating && (
          <div className="text-center py-20">
            <div className="w-12 h-12 border-2 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-zinc-400 text-sm">GoJohnny está montando sua semana...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-950/30 border border-red-800/50 rounded-xl px-4 py-3 text-red-400 text-sm mb-4">
            {error}
          </div>
        )}

        {plan && !generating && (
          <div className="space-y-4">
            {/* Período */}
            <div className="flex items-center justify-between">
              <div>
                <p className="text-zinc-400 text-xs">Semana</p>
                <p className="text-white font-medium">
                  {new Date(plan.week_start + "T12:00:00").toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })}
                  {" — "}
                  {new Date(plan.week_end + "T12:00:00").toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })}
                </p>
              </div>
              <div className="text-right">
                <p className="text-zinc-400 text-xs">Total</p>
                <p className="text-white font-medium">
                  {plan.plan.filter(d => d.tipo !== "descanso").reduce((acc, d) => acc + (d.km || 0), 0).toFixed(1)} km
                </p>
              </div>
            </div>

            {/* Nota do treinador */}
            {plan.coach_notes && (
              <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl px-4 py-3">
                <p className="text-orange-400 text-xs font-medium mb-1">Nota do treinador</p>
                <p className="text-zinc-300 text-sm">{plan.coach_notes}</p>
              </div>
            )}

            {/* Dias */}
            <div className="space-y-3">
              {plan.plan.map((day, i) => (
                <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-semibold capitalize">{day.dia}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full border capitalize ${TYPE_COLORS[day.tipo] || TYPE_COLORS.leve}`}>
                        {day.tipo}
                      </span>
                    </div>
                    {day.tipo !== "descanso" && (
                      <div className="text-right flex-shrink-0">
                        <span className="text-white font-semibold text-sm">{day.km} km</span>
                        {day.pace_sugerido && (
                          <span className="text-zinc-400 text-xs block">{day.pace_sugerido} /km</span>
                        )}
                      </div>
                    )}
                  </div>
                  <p className="text-zinc-400 text-sm">{day.orientacoes}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
