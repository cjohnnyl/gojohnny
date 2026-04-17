# ADR-003 — Migração de Autenticação JWT: HS256/Secret para JWKS/RS256

**Data:** 2026-04-17
**Status:** aceito
**Substitui parcialmente:** ADR-001 (seção de autenticação JWT)
**Impacto:** crítico — resolução de P1 em produção (100% dos usuários bloqueados)

---

## Contexto

O GoJohnny utiliza o Supabase como provedor de autenticação. Os tokens JWT emitidos pelo Supabase são enviados pelo frontend via `Authorization: Bearer <token>` e validados pelo backend FastAPI no Railway.

A implementação original validava os tokens usando `SUPABASE_JWT_SECRET` com o algoritmo **HS256** (HMAC com secret compartilhado). Essa abordagem entrou em conflito com a configuração atual do Supabase, que emite tokens **RS256** (RSA com chave privada/pública). O resultado foi um erro 401 Unauthorized bloqueando 100% dos usuários autenticados em produção.

O Supabase documenta e recomenda oficialmente a validação via **JWKS** (JSON Web Key Set) — endpoint público que expõe as chaves públicas RSA do projeto para verificação de assinaturas RS256.

---

## Decisão

Migrar a validação de JWT no backend de:

- **Antes:** `jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])`
- **Depois:** busca dinâmica das chaves públicas em `SUPABASE_URL/auth/v1/.well-known/jwks.json` + `jwt.decode(token, jwk, algorithms=["RS256"])`

A variável de ambiente `SUPABASE_JWT_SECRET` foi removida da configuração. Apenas `SUPABASE_URL` é necessária.

---

## Alternativas Consideradas

| Alternativa | Prós | Contras | Decisão |
|------------|------|---------|---------|
| **JWKS/RS256 via endpoint público** (escolhida) | Sem secret a gerenciar; rotação de chaves automática; padrão da indústria; recomendado pelo Supabase | I/O em cada request (mitigado com timeout 5s) | ✅ Escolhida |
| Manter HS256 com `SUPABASE_JWT_SECRET` correto | Simples, sem I/O | Secret precisa ser copiado/rotacionado manualmente; conflito confirmado com RS256 do Supabase | ❌ Descartada |
| Cache JWKS em memória | Reduz I/O | Rotação de chaves exige restart; complexidade adicional | ❌ Descartada (iteração futura se houver necessidade) |

---

## Justificativa

A abordagem JWKS/RS256 é a recomendação oficial do Supabase e o padrão da indústria para provedores de identidade modernos. Elimina a necessidade de gerenciar um secret compartilhado, reduz a superfície de ataque e suporta rotação de chaves sem mudança de configuração no backend.

---

## Implementação

**Arquivos modificados:**

| Arquivo | Mudança |
|---------|---------|
| `backend/app/services/deps.py` | Reescrito: `_fetch_jwks()`, `_decode_jwt_with_jwks()`, `get_current_user_id()` |
| `backend/app/core/config.py` | Removido campo `supabase_jwt_secret` |
| `backend/app/main.py` | `_get_user_id_from_token` atualizado para usar `_decode_jwt_with_jwks` |
| `backend/.env` | Removida variável `SUPABASE_JWT_SECRET` |
| `backend/test_migration.py` | Removidas referências a `supabase_jwt_secret` |

**Variável de ambiente necessária no Railway:**

```
SUPABASE_URL=https://<project-ref>.supabase.co
```

`SUPABASE_JWT_SECRET` deve ser removida das variáveis de ambiente do Railway (não é mais lida).

**Fluxo de validação:**

```
Request → Authorization: Bearer <token>
  ↓
GET SUPABASE_URL/auth/v1/.well-known/jwks.json
  ↓
Para cada JWK em keys[]:
  jwt.decode(token, jwk, algorithms=["RS256"])
  ↓ (primeira chave que validar)
Retorna payload["sub"] → user_id
```

**Tratamento de erros:**

| Cenário | HTTP | Mensagem |
|---------|------|----------|
| Token expirado | 401 | "Token expirado" |
| Assinatura inválida / token malformado | 401 | "Token inválido" |
| JWKS indisponível (rede) | 503 | "Serviço de autenticação temporariamente indisponível" |
| JWKS retorna lista vazia | 503 | "Serviço de autenticação com configuração inválida" |
| Token válido sem claim `sub` | 401 | "Token inválido: identificador de usuário ausente" |

---

## Consequências

**Positivas:**
- Erro 401 em produção resolvido — 100% dos usuários desbloqueados
- Sem secret a gerenciar ou vazar
- Rotação de chaves pelo Supabase é transparente para o backend
- Alinhamento com padrão OAuth2/OIDC da indústria

**Negativas / Riscos:**
- `_fetch_jwks()` usa I/O síncrono (`urllib`) em contexto assíncrono — aceitável para volume atual, timeout de 5s configurado. Migrar para `httpx.AsyncClient` se houver latência observável.
- Dependência de disponibilidade do endpoint JWKS do Supabase em cada request autenticado. Em caso de indisponibilidade do Supabase, o backend retorna 503 para usuários autenticados.

---

## Documentos a atualizar

Os documentos abaixo ainda referenciam `SUPABASE_JWT_SECRET` e devem ser atualizados na próxima iteração de documentação:

- `docs/deploy.md`
- `docs/checklist-publicacao.md`
- `docs/variaveis-de-ambiente.md`
- `docs/HANDOFF.md`
- `docs/adr/ADR-001-infraestrutura-supabase.md` (seção de autenticação)
- `.env.example`
