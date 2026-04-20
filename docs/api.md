# API GoJohnny — Documentação de Endpoints

## Autenticação

Todos os endpoints (exceto `/` e `/health`) requerem autenticação via **Bearer Token** (JWT do Supabase):

```
Authorization: Bearer <access_token>
```

O token é obtido via Supabase Auth (login/signup no frontend) e incluído automaticamente pelas requisições do frontend via `lib/api.ts`.

## Health & Status

### GET `/`
Retorna status da aplicação e versão.

**Response:**
```json
{
  "app": "GoJohnny",
  "version": "0.1.0",
  "status": "ok",
  "env": "development"  // só em dev/staging
}
```

### GET `/health`
Health check simples.

**Response:**
```json
{
  "status": "ok"
}
```

---

## Perfil do Corredor

### POST `/profile`
Cria perfil inicial do corredor. Requer autenticação.

**Request:**
```json
{
  "name": "João Silva",
  "level": "intermediário",
  "weekly_volume_km": 30,
  "available_days_per_week": 4,
  "preferred_days": "segunda, quarta, sexta",
  "comfortable_pace": "5:30",
  "main_goal": "Melhorar resistência",
  "injury_history": "Sem lesões prévias",
  "physical_limitations": "Nenhuma",
  "location": "São Paulo, SP",
  "extra_context": "Trabalho como desenvolvedor, treino no fim de semana",
  "target_race_name": "Meia Maratona de SP",
  "target_race_distance_km": 21.1,
  "target_race_date": "2026-06-15"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "João Silva",
  "level": "intermediário",
  "weekly_volume_km": 30,
  "available_days_per_week": 4,
  "preferred_days": "segunda, quarta, sexta",
  "comfortable_pace": "5:30",
  "main_goal": "Melhorar resistência",
  "injury_history": "Sem lesões prévias",
  "physical_limitations": "Nenhuma",
  "location": "São Paulo, SP",
  "extra_context": "Trabalho como desenvolvedor, treino no fim de semana",
  "target_race_name": "Meia Maratona de SP",
  "target_race_distance_km": 21.1,
  "target_race_date": "2026-06-15"
}
```

**Erros:**
- `409 Conflict` - Perfil já existe para este usuário

### GET `/profile`
Retorna perfil do usuário autenticado.

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "João Silva",
  "level": "intermediário",
  "weekly_volume_km": 30,
  "available_days_per_week": 4,
  "preferred_days": "segunda, quarta, sexta",
  "comfortable_pace": "5:30",
  "main_goal": "Melhorar resistência",
  "injury_history": "Sem lesões prévias",
  "physical_limitations": "Nenhuma",
  "location": "São Paulo, SP",
  "extra_context": "Trabalho como desenvolvedor, treino no fim de semana",
  "target_race_name": "Meia Maratona de SP",
  "target_race_distance_km": 21.1,
  "target_race_date": "2026-06-15"
}
```

**Erros:**
- `404 Not Found` - Perfil não encontrado
- `401 Unauthorized` - Token inválido ou expirado

### PUT `/profile`
Atualiza perfil do usuário. Todos os campos são opcionais.

**Request:**
```json
{
  "level": "avançado",
  "weekly_volume_km": 35,
  "main_goal": "Preparação para 10K"
}
```

**Response:** `200 OK` (mesmo formato do GET)

---

## Chat & Conversas

### POST `/chat/message`
Envia mensagem e recebe resposta do treinador (IA).

**Request:**
```json
{
  "content": "Como foi seu treino ontem?",
  "conversation_id": 1  // opcional — se omitido, cria nova conversa
}
```

**Response:** `200 OK`
```json
{
  "conversation_id": 1,
  "message_id": 42,
  "role": "assistant",
  "content": "Ótimo! Vejo que você completou 8km em pace confortável. Como se sentiu durante o treino?",
  "model_used": "gpt-4o-mini",
  "tokens_used": 156,
  "created_at": "2026-04-20T11:45:00Z"
}
```

**Erros:**
- `402 Payment Required` - Saldo insuficiente na conta OpenAI
- `502 Bad Gateway` - Erro ao comunicar com IA
- `404 Not Found` - Conversa não encontrada (se `conversation_id` inválido)

**Timeout:** 30 segundos (IA pode levar tempo para responder)

### GET `/chat/conversations`
Lista todas as conversas do usuário (ordenadas por mais recentes).

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Como foi seu treino ontem?",
    "created_at": "2026-04-20T10:00:00Z",
    "updated_at": "2026-04-20T11:45:00Z"
  },
  {
    "id": 2,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Dúvida sobre estratégia de 10K",
    "created_at": "2026-04-19T14:30:00Z",
    "updated_at": "2026-04-19T14:35:00Z"
  }
]
```

### GET `/chat/conversations/{conversation_id}/messages`
Retorna histórico completo de uma conversa.

**Response:** `200 OK`
```json
[
  {
    "role": "user",
    "content": "Como foi seu treino ontem?",
    "created_at": "2026-04-20T10:00:00Z"
  },
  {
    "role": "assistant",
    "content": "Ótimo! Vejo que você completou 8km...",
    "created_at": "2026-04-20T10:05:00Z"
  }
]
```

**Erros:**
- `404 Not Found` - Conversa não encontrada

---

## Planos de Treino

### POST `/plans/generate`
Gera novo plano de treino para a semana atual baseado no perfil.

**Request:** Sem body (usa perfil do usuário)

**Response:** `201 Created`
```json
{
  "id": 5,
  "week_start": "2026-04-21",
  "week_end": "2026-04-27",
  "coach_notes": "Esta semana fokamos em recuperação após a prova de 5K.",
  "plan": {
    "segunda": {
      "tipo": "recuperação",
      "distancia": "6km",
      "pace": "6:30-7:00",
      "detalhes": "Trote leve, foco em recuperação"
    },
    "terça": {
      "tipo": "intervalo",
      "distancia": "8km",
      "detalhes": "5x 800m em ritmo de prova + 400m recuperação"
    }
    // ... outros dias
  },
  "tokens_used": 450
}
```

**Erros:**
- `402 Payment Required` - Saldo insuficiente OpenAI
- `422 Unprocessable Entity` - Perfil não encontrado (crie em POST /profile primeiro)
- `502 Bad Gateway` - Erro ao gerar plano com IA

**Timeout:** 30 segundos

### GET `/plans/current`
Retorna plano ativo da semana atual.

**Response:** `200 OK`
```json
{
  "id": 5,
  "week_start": "2026-04-21",
  "week_end": "2026-04-27",
  "coach_notes": "Esta semana fokamos em recuperação após a prova de 5K.",
  "plan": {
    "segunda": {
      "tipo": "recuperação",
      "distancia": "6km",
      "pace": "6:30-7:00",
      "detalhes": "Trote leve, foco em recuperação"
    },
    "terça": {
      "tipo": "intervalo",
      "distancia": "8km",
      "detalhes": "5x 800m em ritmo de prova + 400m recuperação"
    }
    // ... outros dias
  }
}
```

**Erros:**
- `404 Not Found` - Nenhum plano ativo para esta semana

### GET `/plans`
Lista todos os planos do usuário (últimas 12 semanas, ordenadas decrescente).

**Response:** `200 OK`
```json
[
  {
    "id": 5,
    "week_start": "2026-04-21",
    "week_end": "2026-04-27",
    "status": "active",
    "coach_notes": "Esta semana fokamos em recuperação..."
  },
  {
    "id": 4,
    "week_start": "2026-04-14",
    "week_end": "2026-04-20",
    "status": "active",
    "coach_notes": "Semana de pico antes da prova..."
  }
]
```

---

## Feedback de Treino

### POST `/feedback`
Registra feedback após um treino (sensações, dor, cansaço, etc).

**Request:**
```json
{
  "training_date": "2026-04-20",
  "effort_rating": 7,              // 1-10
  "pain_level": 2,                 // 0-10 (0 = sem dor)
  "sleep_quality": 8,              // 1-10
  "general_feeling": "Muito bem",  // descrição
  "notes": "Joelhos um pouco cansados",
  "plan_id": 5                     // opcional
}
```

**Response:** `201 Created`
```json
{
  "id": 10,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_id": 5,
  "training_date": "2026-04-20",
  "effort_rating": 7,
  "pain_level": 2,
  "sleep_quality": 8,
  "general_feeling": "Muito bem",
  "notes": "Joelhos um pouco cansados",
  "ai_analysis": "Análise IA do feedback...",
  "load_recommendation": "Reduza intensidade próxima semana",
  "created_at": "2026-04-20T20:30:00Z"
}
```

**Erros:**
- `404 Not Found` - Plan ID não encontrado ou não pertence ao usuário

### GET `/feedback`
Lista últimos 30 feedbacks do usuário (ordenados decrescente por data).

**Response:** `200 OK`
```json
[
  {
    "id": 10,
    "training_date": "2026-04-20",
    "effort_rating": 7,
    "pain_level": 2,
    "sleep_quality": 8,
    "general_feeling": "Muito bem",
    "ai_analysis": "Análise IA...",
    "created_at": "2026-04-20T20:30:00Z"
  }
]
```

### GET `/feedback/{feedback_id}`
Retorna um feedback específico.

**Response:** `200 OK` (mesmo formato)

**Erros:**
- `404 Not Found` - Feedback não encontrado

---

## Memória do Corredor

### GET `/memory`
Retorna estado completo da memória do corredor (contexto mantido pela IA).

**Response:** `200 OK`
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "active_plan_id": 5,
  "plan_week_current": 2,
  "plan_week_total": 12,
  "week_progress": {
    "segunda": "done",
    "terça": "done",
    "quarta": "pending",
    "quinta": "skipped",
    "sexta": "pending",
    "sábado": "pending",
    "domingo": "pending"
  },
  "recent_feedbacks": [
    { "date": "2026-04-20", "effort": 7, "pain": 2 }
  ],
  "physical_alerts": ["joelhos_cansados"],
  "load_adjustments": ["reduzir_intensidade_semana_proxima"],
  "chat_observations": [
    "Corredor prefere treinos de manhã",
    "Tem dificuldade com intervalos longos"
  ],
  "last_coaching_style": "Motivacional",
  "last_session_summary": "Feedback positivo, recuperação OK",
  "last_session_at": "2026-04-20T20:30:00Z"
}
```

### PATCH `/memory/week-progress`
Atualiza progresso de um dia da semana.

**Request:**
```json
{
  "day": "segunda",
  "status": "done"  // done | skipped | pending
}
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "day": "segunda",
  "status": "done"
}
```

**Erros:**
- `422 Unprocessable Entity` - Status inválido

### PATCH `/memory/observations`
Adiciona observação capturada no chat (máx 200 caracteres).

**Request:**
```json
{
  "note": "Corredor tem preferência por treinos ao amanhecer"
}
```

**Response:** `200 OK`
```json
{
  "ok": true,
  "note": "Corredor tem preferência por treinos ao amanhecer"
}
```

**Erros:**
- `422 Unprocessable Entity` - Note vazio ou > 200 caracteres

---

## Rate Limiting

- Limite padrão: por IP ou user_id (extraído do JWT)
- Endpoints sensíveis: `/chat/message`, `/plans/generate` têm limite reduzido
- Resposta ao limite: `429 Too Many Requests`

---

## Exemplos com curl

### Login e obter token (Supabase)
```bash
curl -X POST https://your-project.supabase.co/auth/v1/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password",
    "grant_type": "password"
  }' | jq '.access_token'
```

### Criar perfil
```bash
TOKEN="seu-access-token"
curl -X POST http://localhost:8000/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "level": "intermediário",
    "weekly_volume_km": 30,
    "available_days_per_week": 4,
    "preferred_days": "segunda, quarta, sexta",
    "comfortable_pace": "5:30",
    "main_goal": "Melhorar resistência",
    "injury_history": "Sem lesões prévias",
    "physical_limitations": "Nenhuma",
    "location": "São Paulo, SP",
    "extra_context": "Trabalho como desenvolvedor",
    "target_race_name": "Meia Maratona de SP",
    "target_race_distance_km": 21.1,
    "target_race_date": "2026-06-15"
  }'
```

### Enviar mensagem no chat
```bash
TOKEN="seu-access-token"
curl -X POST http://localhost:8000/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Como foi seu treino ontem?"
  }'
```

### Gerar plano de treino
```bash
TOKEN="seu-access-token"
curl -X POST http://localhost:8000/plans/generate \
  -H "Authorization: Bearer $TOKEN"
```

### Submeter feedback
```bash
TOKEN="seu-access-token"
curl -X POST http://localhost:8000/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "training_date": "2026-04-20",
    "effort_rating": 7,
    "pain_level": 2,
    "sleep_quality": 8,
    "general_feeling": "Muito bem",
    "notes": "Joelhos um pouco cansados"
  }'
```

---

## Códigos de Status HTTP

| Código | Significado | Quando |
|--------|-------------|--------|
| 200 | OK | Sucesso em GET/PUT |
| 201 | Created | Sucesso em POST |
| 204 | No Content | Sucesso sem resposta |
| 400 | Bad Request | Request malformado |
| 401 | Unauthorized | Token inválido/expirado |
| 402 | Payment Required | Saldo insuficiente OpenAI |
| 404 | Not Found | Recurso não existe |
| 409 | Conflict | Conflito (ex: perfil já existe) |
| 422 | Unprocessable Entity | Validação falhou |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Erro do servidor |
| 502 | Bad Gateway | Erro ao comunicar com serviço externo |
