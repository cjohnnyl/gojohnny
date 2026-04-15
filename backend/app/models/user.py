"""
Model User — Descontinuado

Usuários agora são gerenciados exclusivamente pelo Supabase Auth (auth.users).
Este arquivo é mantido como stub para evitar quebra de imports em código legado.

Migração:
- user_id agora é String(36) referenciando auth.users.id do Supabase
- Todas as tabelas removem FK para users.id
- Autenticação via JWT do Supabase, não mais via password_hash local
"""

# Importações neste arquivo foram removidas — modelo obsoleto
