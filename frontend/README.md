# Frontend GoJohnny

Frontend do GoJohnny — treinador digital de corrida de rua. Aplicação Next.js com autenticação via Supabase e integração com API backend em FastAPI.

## O que é

Interface web do GoJohnny onde corredores podem:
- Fazer login/signup via Supabase Auth
- Criar e atualizar seu perfil de corredor
- Conversar com o treinador IA (chat interativo)
- Visualizar e gerar planos de treino semanais
- Registrar feedback pós-treino

## Stack Técnica

- **Next.js 15** - Framework React com App Router
- **React 19** - Componentes UI
- **TypeScript** - Type safety
- **Supabase JS SDK** - Autenticação e integração
- **Tailwind CSS v4** - Estilização
- **ESLint** - Code quality

## Estrutura de Pastas

```
frontend/
├── app/
│   ├── page.tsx              # Home
│   ├── layout.tsx            # Root layout (providers)
│   ├── middleware.ts         # Proteção de rotas (redirect para login)
│   ├── auth/
│   │   ├── login/page.tsx    # Login
│   │   ├── reset-password/   # Reset de senha
│   │   ├── callback/route.ts # Callback Supabase
│   │   └── auth-error/page.tsx
│   ├── chat/page.tsx         # Chat com IA
│   ├── onboarding/page.tsx   # Criar perfil
│   ├── plano/page.tsx        # Planos de treino
│   ├── components/
│   │   ├── ChatSidebar.tsx   # Sidebar com histórico de conversas
│   │   └── UserMenu.tsx      # Menu do usuário
│   └── globals.css           # Estilos globais
├── lib/
│   ├── api.ts               # Cliente HTTP com autenticação automática
│   ├── supabase.ts          # Cliente Supabase (lado cliente)
│   └── supabase-server.ts   # Supabase SSR (middleware)
├── public/                  # Assets estáticos
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.mjs
└── next.config.ts
```

## Como Rodar Localmente

### 1. Variáveis de Ambiente

As variáveis estão no `.env.example` na **raiz do projeto** (não neste diretório). Copie para `.env.local` nesta pasta ou configure direto:

```bash
# frontend/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Instalar Dependências

```bash
npm install
```

### 3. Rodar Dev Server

```bash
npm run dev
```

Acesse em: `http://localhost:3000`

### 4. Build para Produção

```bash
npm run build
npm start
```

## Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | URL do projeto Supabase | `https://abc.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Chave anon do Supabase | `eyJhbGc...` |
| `NEXT_PUBLIC_API_URL` | URL base da API backend | `http://localhost:8000` ou `https://...railway.app` |

**Nota:** Prefixo `NEXT_PUBLIC_` significa que as variáveis são expostas no frontend (seguro pois são chaves anon). Nunca coloque secrets aqui.

## Integração com Backend

O frontend se conecta ao backend via `lib/api.ts`:

1. **Autenticação:** Usa Supabase Auth para fazer login/signup
2. **Requisições:** Todas as chamadas incluem `Authorization: Bearer <token>` automaticamente
3. **Refresh automático:** Se token expirar, Supabase JS SDK renovar automaticamente
4. **Logout automático:** Se backend retornar 401, frontend faz logout automático

Endpoints principais (veja `../docs/api.md` para documentação completa):
- `POST /profile` - Criar/atualizar perfil
- `POST /chat/message` - Enviar mensagem
- `POST /plans/generate` - Gerar plano
- `POST /feedback` - Submeter feedback

## Desenvolvimento

### ESLint

```bash
npm run lint
```

### Type Checking

TypeScript é compilado automaticamente durante `npm run dev` e `npm run build`.

## Deploy em Produção

O frontend é deployado em **Vercel**:

```bash
# Conectar repo ao Vercel (via dashboard)
# Variáveis de ambiente configuradas no Vercel

vercel deploy --prod
```

Variáveis no Vercel:
- `NEXT_PUBLIC_SUPABASE_URL` (prod)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` (prod)
- `NEXT_PUBLIC_API_URL` (URL do backend em produção, ex: `https://...railway.app`)

## Convenções

- **Componentes:** `PascalCase` (ex: `ChatSidebar.tsx`)
- **Utilities/hooks:** `camelCase` (ex: `useAuth.ts`)
- **Arquivos:** `kebab-case` para rotas dinâmicas (ex: `[id].tsx`)
- **Type hints:** Sempre com TypeScript, sem `any`

## Troubleshooting

### CORS error
- Verificar se `NEXT_PUBLIC_API_URL` está correto
- Verificar se backend permite origem do frontend em `ALLOWED_ORIGINS`

### 401 Unauthorized
- Token expirado — fazer login novamente
- Verificar se `NEXT_PUBLIC_SUPABASE_URL` e `NEXT_PUBLIC_SUPABASE_ANON_KEY` estão corretos

### Backend não responde
- Verificar se backend está rodando em `http://localhost:8000`
- Verificar se frontend consegue fazer ping: `curl http://localhost:8000/health`

## Referências

- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase JS SDK](https://supabase.com/docs/reference/javascript)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [API GoJohnny](../docs/api.md)
