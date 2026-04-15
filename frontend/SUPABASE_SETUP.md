# Configuração do Supabase — GoJohnny Frontend

Este guia descreve como configurar o Supabase para autenticação do GoJohnny.

## O que foi implementado

- **Autenticação com Supabase Auth**: Substitui o JWT próprio pelo Supabase
- **Gerenciamento de sessão**: Cookies automaticamente gerenciados pelo Supabase SSR
- **Renovação de token automática**: Sem necessidade de refresh manual
- **Reset de senha**: Fluxo completo com email e redirecionamento
- **Confirmação de email**: Link de callback para ativar conta após registro

## Pré-requisitos

- Conta no [Supabase](https://supabase.com)
- Projeto Supabase criado

## Passo 1: Criar projeto Supabase

1. Acesse [supabase.com](https://supabase.com)
2. Crie um novo projeto (ou use um existente)
3. Vá até **Project Settings > API**
4. Anote:
   - **Project URL** (ex: `https://your-project.supabase.co`)
   - **Anon Public Key** (ex: `eyJhbGciOiJIUzI1...`)

## Passo 2: Configurar variáveis de ambiente

Crie um arquivo `.env.local` na raiz do projeto `frontend/`:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1...
NEXT_PUBLIC_API_URL=http://localhost:8011
```

**Nota:** Substitua os valores pelos seus dados reais. `NEXT_PUBLIC_*` significa que esses valores serão visíveis no frontend (como devem ser — são públicos).

## Passo 3: Configurar Auth no Supabase

### 3.1 — Habilitar Email/Password

1. No painel Supabase, vá até **Authentication > Providers**
2. Procure por **Email**
3. Ative e configure:
   - **Confirm email**: Ativado (obrigatório)
   - **Enable autoconfirm**: Desativado (os usuários devem confirmar o email)

### 3.2 — Configurar URLs de redirecionamento

1. Vá até **Authentication > URL Configuration**
2. Em **Site URL**, adicione:
   - `http://localhost:3000` (desenvolvimento local)
   - `https://seu-dominio.com` (produção)

3. Em **Redirect URLs**, adicione:
   - `http://localhost:3000/auth/callback`
   - `http://localhost:3000/auth/reset-password`
   - `https://seu-dominio.com/auth/callback`
   - `https://seu-dominio.com/auth/reset-password`

### 3.3 — Configurar SMTP (Emails)

Para enviar emails de confirmação e reset de senha:

1. No painel Supabase, vá até **Authentication > Email Templates**
2. Configure o seu próprio SMTP ou use o do Supabase:
   - Se usar o padrão do Supabase, apenas verifique que está habilitado
   - Se usar SMTP próprio, configure as credenciais

**Nota para produção:** O Supabase por padrão usa limites de taxa para emails. Para produção, configure um serviço de email externo (SendGrid, Resend, etc).

## Passo 4: Backend — Validação de token

O backend **DEVE** validar o token Supabase nas requisições:

```python
from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Em cada rota protegida:
def get_current_user(token: str):
    try:
        user = supabase.auth.get_user(token)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
```

O frontend envia: `Authorization: Bearer {token}`

O backend valida usando o Supabase Python client ou fazendo chamadas diretas à API do Supabase.

## Passo 5: Instalar dependências

```bash
npm install
# ou
yarn install
# ou
pnpm install
```

## Testando localmente

```bash
npm run dev
```

1. Acesse `http://localhost:3000/login`
2. Clique em **Criar conta**
3. Digite email e senha
4. Você receberá um email de confirmação
5. Clique no link de confirmação (será redirecionado para `/chat`)
6. Se você tiver um perfil no backend, a conversa iniciará com seu nome
7. Se não, a conversa começará com onboarding conversacional

### Para testar reset de senha:

1. Na página de login, clique em **Esqueci minha senha**
2. Digite seu email
3. Você receberá um email com um link
4. Clique e defina sua nova senha
5. Será redirecionado para login

## Fluxo de autenticação

### Login/Registro

```
[Frontend: form] → [Supabase Auth] → [Cookies do navegador] → [Middleware Supabase SSR] → [Rota protegida]
```

### Renovação de token

```
Automática: Supabase SSR gerencia a renovação baseado na expiração do refresh token
```

### Logout

```
[Frontend: signOut()] → [Supabase] → [Cookies limpos] → [Redirecionado para /login]
```

## Troubleshooting

### "Erro ao criar conta"

- Verifique se o email é válido
- Verifique se a senha tem no mínimo 6 caracteres
- Procure por rate limiting do Supabase (máx de 30 inscrições por hora por IP)

### "Email de confirmação não chega"

- Verifique a pasta de Spam
- Verif ique se o SMTP está configurado corretamente
- Logue no painel Supabase e procure por logs de email em **Logs > Auth**

### "Sessão expirada ao carregar a página"

- Isso é esperado se o refresh token expirou (padrão: 7 dias)
- O usuário será redirecionado para `/login` automaticamente
- O middleware Supabase SSR trata isso

### "401 Unauthorized" em requisições ao backend

- Verifique se o token está sendo enviado no header `Authorization: Bearer {token}`
- Verifique se o backend está validando com o Supabase corretamente
- Verifique se as chaves do Supabase no backend estão corretas

## Próximas etapas

1. Configurar email de produção (SendGrid, Resend, etc)
2. Adicionar autenticação via OAuth (Google, GitHub, etc) - opcional
3. Adicionar 2FA - opcional
4. Implementar lógica de role/permissões no Supabase RLS - futuro

## Referências

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Supabase SSR Docs](https://supabase.com/docs/guides/auth/server-side-rendering)
- [Supabase Email Docs](https://supabase.com/docs/guides/auth/server-side-rendering#email-verification)
