"""Integração com Claude API — coração do GoJohnny."""
from typing import Optional

import anthropic
from loguru import logger

from ..core.config import get_settings
from ..models.runner_profile import RunnerProfile

settings = get_settings()
_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

# System prompt base — define identidade, tom e guardrails do GoJohnny
_SYSTEM_BASE = """Você é o GoJohnny, um treinador digital especialista em corrida de rua.

Seu papel é ajudar o corredor a evoluir com segurança, melhorar sua performance, evitar lesões e se preparar melhor para treinos e provas.

Tom: direto, técnico, didático e motivador. Firme quando necessário.
Idioma: sempre português do Brasil.

GUARDRAILS OBRIGATÓRIOS:
- Nunca diagnostique lesões nem prescreva tratamento médico.
- Nunca substitua médico, nutricionista, fisioterapeuta ou profissional de saúde.
- Se o corredor relatar dor forte, piora importante, mal-estar relevante ou sinais de risco, oriente busca imediata por profissional qualificado.
- Não faça recomendações agressivas de volume, intensidade ou recuperação.
- Não incentive comportamento de risco.
- Mantenha foco exclusivo em corrida de rua, treinos, provas, recuperação, clima, rotas e equipamentos.
- Se o usuário puxar assunto fora do escopo, redirecione com educação.
- Use linguagem inclusiva. Não assuma gênero, idade, corpo, renda ou nível atlético sem contexto.
- Quando estiver inferindo algo, deixe claro.
- Peça informação adicional quando faltar contexto crítico.

PRINCÍPIO CENTRAL:
Você não é um gerador de respostas genéricas. Você usa o contexto real do corredor para dar orientação prática, contextual e progressiva."""


def _build_context_block(profile: Optional[RunnerProfile]) -> str:
    """Monta o bloco de contexto do corredor para o system prompt."""
    if not profile:
        return "\nO corredor ainda não preencheu o perfil. Quando relevante, pergunte sobre nível, objetivo, disponibilidade e histórico de lesões antes de recomendar algo mais sensível.\n"

    lines = ["\n--- CONTEXTO DO CORREDOR ---"]

    lines.append(f"Nome: {profile.name}")
    lines.append(f"Nível: {profile.level}")

    if profile.main_goal:
        lines.append(f"Objetivo principal: {profile.main_goal}")
    if profile.weekly_volume_km:
        lines.append(f"Volume semanal atual: {profile.weekly_volume_km} km")
    if profile.available_days_per_week:
        lines.append(f"Dias disponíveis por semana: {profile.available_days_per_week}")
    if profile.preferred_days:
        lines.append(f"Dias preferidos: {profile.preferred_days}")
    if profile.comfortable_pace:
        lines.append(f"Pace confortável: {profile.comfortable_pace} min/km")
    if profile.target_race_name:
        lines.append(f"Prova alvo: {profile.target_race_name}")
    if profile.target_race_distance_km:
        lines.append(f"Distância da prova: {profile.target_race_distance_km} km")
    if profile.target_race_date:
        lines.append(f"Data da prova: {profile.target_race_date}")
    if profile.injury_history:
        lines.append(f"Histórico de lesões: {profile.injury_history}")
    if profile.physical_limitations:
        lines.append(f"Limitações físicas: {profile.physical_limitations}")
    if profile.location:
        lines.append(f"Localização: {profile.location}")
    if profile.extra_context:
        lines.append(f"Contexto adicional: {profile.extra_context}")

    lines.append("--- FIM DO CONTEXTO ---\n")
    return "\n".join(lines)


def chat(
    messages: list[dict],
    profile: Optional[RunnerProfile] = None,
    model: Optional[str] = None,
) -> tuple[str, int]:
    """
    Envia mensagens para Claude e retorna (resposta, tokens_usados).

    messages: lista de {"role": "user"|"assistant", "content": str}
    """
    model = model or settings.anthropic_model_chat
    system = _SYSTEM_BASE + _build_context_block(profile)

    logger.debug(f"Chamando Claude [{model}] com {len(messages)} mensagens")

    response = _client.messages.create(
        model=model,
        max_tokens=settings.anthropic_max_tokens,
        system=system,
        messages=messages,
    )

    content = response.content[0].text
    tokens = response.usage.input_tokens + response.usage.output_tokens

    logger.info(f"Claude respondeu — tokens usados: {tokens}")
    return content, tokens


def generate_training_plan(profile: RunnerProfile) -> tuple[str, int]:
    """Gera planilha semanal de treino usando Claude Sonnet."""
    prompt = f"""Com base no contexto do corredor abaixo, gere uma planilha semanal de treino.

Retorne um JSON válido com a seguinte estrutura:
{{
  "semana": "descrição resumida da semana",
  "coach_notes": "observação geral do treinador",
  "dias": [
    {{
      "dia": "segunda",
      "tipo": "leve|regenerativo|ritmo|intervalado|longao|descanso",
      "km": 5.0,
      "pace_sugerido": "6:30",
      "orientacoes": "instrução prática de execução"
    }}
  ]
}}

Inclua apenas os dias de treino disponíveis. Inclua dias de descanso explicitamente.
Responda APENAS com o JSON, sem texto adicional."""

    content, tokens = chat(
        messages=[{"role": "user", "content": prompt}],
        profile=profile,
        model=settings.anthropic_model_coach,
    )
    return content, tokens


def analyze_feedback(
    profile: Optional[RunnerProfile],
    effort: Optional[int],
    pain: Optional[int],
    sleep: Optional[int],
    feeling: Optional[str],
    notes: Optional[str],
) -> tuple[str, str, int]:
    """
    Analisa feedback pós-treino.
    Retorna (analise, recomendacao: maintain|reduce|increase, tokens).
    """
    prompt = f"""Analise o feedback pós-treino abaixo e retorne um JSON com:
{{
  "analise": "análise curta e prática em 2-3 frases",
  "recomendacao": "maintain|reduce|increase"
}}

Feedback:
- Percepção de esforço (1-10): {effort}
- Dor/desconforto (0-10): {pain}
- Qualidade do sono (1-5): {sleep}
- Sensação geral: {feeling}
- Notas do corredor: {notes or 'Nenhuma'}

Responda APENAS com o JSON."""

    content, tokens = chat(
        messages=[{"role": "user", "content": prompt}],
        profile=profile,
        model=settings.anthropic_model_coach,
    )
    return content, tokens
