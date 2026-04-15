"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

const LEVELS = [
  { value: "beginner", label: "Iniciante", desc: "Estou começando a correr" },
  { value: "intermediate", label: "Intermediário", desc: "Corro regularmente há algum tempo" },
  { value: "advanced", label: "Avançado", desc: "Treino com consistência e volume alto" },
];

const GOALS = [
  { value: "consistency", label: "Ganhar consistência" },
  { value: "complete_5k", label: "Completar 5K" },
  { value: "complete_10k", label: "Completar 10K" },
  { value: "complete_21k", label: "Completar 21K" },
  { value: "improve_time", label: "Melhorar meu tempo" },
  { value: "other", label: "Outro" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // BUG-05: protege a rota contra acesso sem autenticação.
  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("access_token")) {
      router.push("/login");
    }
  }, [router]);

  const [form, setForm] = useState({
    name: "",
    level: "",
    main_goal: "",
    available_days_per_week: 3,
    weekly_volume_km: "",
    comfortable_pace: "",
    target_race_name: "",
    target_race_distance_km: "",
    target_race_date: "",
    injury_history: "",
    location: "",
  });

  function set(field: string, value: unknown) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleFinish() {
    // BUG-03: valida campos obrigatórios antes de chamar a API.
    if (!form.name || !form.level) {
      setError(
        !form.name
          ? "Por favor, informe seu nome antes de continuar."
          : "Por favor, selecione seu nível como corredor antes de continuar."
      );
      return;
    }

    setLoading(true);
    setError("");
    try {
      const payload = {
        ...form,
        weekly_volume_km: form.weekly_volume_km ? Number(form.weekly_volume_km) : undefined,
        target_race_distance_km: form.target_race_distance_km
          ? Number(form.target_race_distance_km)
          : undefined,
        target_race_date: form.target_race_date || undefined,
        injury_history: form.injury_history || undefined,
        location: form.location || undefined,
        comfortable_pace: form.comfortable_pace || undefined,
        target_race_name: form.target_race_name || undefined,
      };
      await api.createProfile(payload);
      router.push("/chat");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao salvar perfil");
    } finally {
      setLoading(false);
    }
  }

  const totalSteps = 3;

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">Vamos te conhecer</h1>
          <p className="text-zinc-400 text-sm mt-2">
            Etapa {step} de {totalSteps} — Quanto mais contexto, melhor o treino
          </p>
          {/* Progress bar */}
          <div className="mt-4 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-1.5 rounded-full transition-all"
              style={{
                width: `${(step / totalSteps) * 100}%`,
                background: "linear-gradient(90deg, #7c3aed, #a855f7)",
              }}
            />
          </div>
        </div>

        <div
          className="bg-zinc-900/50 rounded-3xl p-8 border border-zinc-800"
          style={{
            boxShadow: "0 0 40px rgba(124, 58, 237, 0.08)",
          }}
        >
          {/* Step 1 — Identidade */}
          {step === 1 && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-white">Quem é você?</h2>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Nome</label>
                <input
                  className="input"
                  placeholder="Como posso te chamar?"
                  value={form.name}
                  onChange={(e) => set("name", e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Nível como corredor</label>
                <div className="space-y-2">
                  {LEVELS.map((l) => (
                    <button
                      key={l.value}
                      onClick={() => set("level", l.value)}
                      className={`w-full text-left p-3 rounded-lg border transition-all ${
                        form.level === l.value
                          ? "border-violet-500 text-white"
                          : "border-zinc-700 text-zinc-300 hover:border-zinc-600"
                      }`}
                      style={
                        form.level === l.value
                          ? {
                              background: "rgba(124, 58, 237, 0.12)",
                            }
                          : {}
                      }
                    >
                      <span className="font-medium">{l.label}</span>
                      <span className="text-sm text-zinc-400 block">{l.desc}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Cidade (opcional)</label>
                <input
                  className="input"
                  placeholder="Ex: Santo André, SP"
                  value={form.location}
                  onChange={(e) => set("location", e.target.value)}
                />
              </div>
            </div>
          )}

          {/* Step 2 — Treino */}
          {step === 2 && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-white">Seu treino atual</h2>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Objetivo principal</label>
                <div className="grid grid-cols-2 gap-2">
                  {GOALS.map((g) => (
                    <button
                      key={g.value}
                      onClick={() => set("main_goal", g.value)}
                      className={`p-2.5 rounded-lg border text-sm transition-all ${
                        form.main_goal === g.value
                          ? "border-violet-500 text-white"
                          : "border-zinc-700 text-zinc-300 hover:border-zinc-600"
                      }`}
                      style={
                        form.main_goal === g.value
                          ? {
                              background: "rgba(124, 58, 237, 0.12)",
                            }
                          : {}
                      }
                    >
                      {g.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-1">
                  Dias disponíveis por semana: <span className="text-white font-medium">{form.available_days_per_week}</span>
                </label>
                <input
                  type="range"
                  min={1}
                  max={7}
                  value={form.available_days_per_week}
                  onChange={(e) => set("available_days_per_week", Number(e.target.value))}
                  className="w-full accent-violet-500"
                />
                <div className="flex justify-between text-xs text-zinc-500 mt-1">
                  <span>1</span><span>7</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Volume semanal (km)</label>
                  <input
                    className="input"
                    type="number"
                    placeholder="Ex: 30"
                    value={form.weekly_volume_km}
                    onChange={(e) => set("weekly_volume_km", e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Pace confortável</label>
                  <input
                    className="input"
                    placeholder="Ex: 5:45"
                    value={form.comfortable_pace}
                    onChange={(e) => set("comfortable_pace", e.target.value)}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 3 — Prova e histórico */}
          {step === 3 && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold text-white">Prova e histórico</h2>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Prova alvo (opcional)</label>
                <input
                  className="input"
                  placeholder="Ex: Meia Maratona de Santo André"
                  value={form.target_race_name}
                  onChange={(e) => set("target_race_name", e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Distância (km)</label>
                  <input
                    className="input"
                    type="number"
                    placeholder="Ex: 21"
                    value={form.target_race_distance_km}
                    onChange={(e) => set("target_race_distance_km", e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Data da prova</label>
                  <input
                    className="input"
                    type="date"
                    value={form.target_race_date}
                    onChange={(e) => set("target_race_date", e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  Histórico de lesões (opcional)
                </label>
                <textarea
                  className="input resize-none"
                  rows={3}
                  placeholder="Ex: Tendinite no joelho direito em 2024, já recuperada"
                  value={form.injury_history}
                  onChange={(e) => set("injury_history", e.target.value)}
                />
              </div>
            </div>
          )}

          {error && (
            <p className="mt-4 text-red-400 text-sm bg-red-950/30 border border-red-800/50 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          {/* Nav */}
          <div className="flex gap-3 mt-8">
            {step > 1 && (
              <button
                onClick={() => setStep((s) => s - 1)}
                className="flex-1 py-3 rounded-lg border border-zinc-700 text-zinc-300 hover:border-violet-500 hover:text-violet-400 transition-colors font-medium"
              >
                Voltar
              </button>
            )}
            {step < totalSteps ? (
              <button
                onClick={() => setStep((s) => s + 1)}
                disabled={
                  step === 1
                    ? !form.name || !form.level
                    : step === 2
                    ? !form.main_goal
                    : false
                }
                className="flex-1 text-white font-semibold py-3 rounded-lg transition-all disabled:opacity-40"
                style={{
                  background: "linear-gradient(135deg, #7c3aed, #a855f7)",
                }}
              >
                Continuar
              </button>
            ) : (
              <button
                onClick={handleFinish}
                disabled={loading || !form.main_goal}
                className="flex-1 text-white font-semibold py-3 rounded-lg transition-all disabled:opacity-40"
                style={{
                  background: "linear-gradient(135deg, #7c3aed, #a855f7)",
                }}
              >
                {loading ? "Salvando..." : "Começar"}
              </button>
            )}
          </div>
        </div>
      </div>

      <style jsx global>{`
        .input {
          width: 100%;
          background: rgba(39, 39, 42, 0.5);
          border: 1px solid rgb(63, 63, 70);
          border-radius: 0.5rem;
          padding: 0.625rem 1rem;
          color: white;
          font-size: 0.875rem;
          outline: none;
        }
        .input:focus {
          border-color: rgb(124, 58, 237);
          box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2);
        }
        .input::placeholder {
          color: rgb(113, 113, 122);
        }
      `}</style>
    </div>
  );
}
