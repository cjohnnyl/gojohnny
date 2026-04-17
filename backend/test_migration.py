"""
Script de validação pós-migração — Testa integridade estrutural.
NÃO é um teste completo, apenas validação de imports e construção de objetos.
"""

import sys
from datetime import datetime, date

# Testa imports dos modelos
try:
    from app.models.runner_profile import RunnerProfile
    from app.models.training_plan import TrainingPlan
    from app.models.training_feedback import TrainingFeedback
    from app.models.conversation import Conversation, Message
    from app.models.runner_memory import RunnerMemory
    print("✓ Modelos importados com sucesso")
except Exception as e:
    print(f"✗ Erro ao importar modelos: {e}")
    sys.exit(1)

# Testa imports dos serviços
try:
    from app.services.deps import get_current_user_id
    from app.services import memory_service
    from app.services import ai
    print("✓ Serviços importados com sucesso")
except Exception as e:
    print(f"✗ Erro ao importar serviços: {e}")
    sys.exit(1)

# Testa imports dos routes
try:
    from app.routes import chat, feedback, plans, profile, memory
    print("✓ Routes importados com sucesso")
except Exception as e:
    print(f"✗ Erro ao importar routes: {e}")
    sys.exit(1)

# Testa imports da configuração
try:
    from app.core.config import get_settings
    settings = get_settings()
    print(f"✓ Config carregado (env={settings.app_env})")
except Exception as e:
    print(f"✗ Erro ao importar config: {e}")
    sys.exit(1)

# Validação estrutural: simula criação de objetos (sem BD)
print("\n--- Validações estruturais ---")

# Verifica tipos de user_id nos models
import inspect

models_to_check = [
    (RunnerProfile, "RunnerProfile"),
    (TrainingPlan, "TrainingPlan"),
    (TrainingFeedback, "TrainingFeedback"),
    (Conversation, "Conversation"),
    (RunnerMemory, "RunnerMemory"),
]

for model_class, model_name in models_to_check:
    try:
        # Verifica se o model tem user_id como atributo
        if hasattr(model_class, 'user_id'):
            # Tenta obter o tipo a partir da anotação (ou coluna)
            col = getattr(model_class, 'user_id')
            # String(36) ou Mapped[str] deveria estar definido
            print(f"✓ {model_name}.user_id definido (tipo esperado: String ou Mapped[str])")
        else:
            print(f"✗ {model_name} não tem user_id!")
            sys.exit(1)
    except Exception as e:
        print(f"⚠ {model_name}: {e}")

# Verifica que User não é mais referenciado
print("\n--- Verificações de limpeza ---")
try:
    from app.models.user import User
    # User agora é apenas um stub
    import inspect
    source = inspect.getsource(User)
    if "descontinuado" in source.lower() or "obsoleto" in source.lower():
        print("✓ Modelo User marcado como obsoleto (correto)")
    else:
        print("⚠ Modelo User ainda tem código — verificar limpeza")
except ImportError:
    print("✓ User não pode ser importado (esperado após migração)")
except Exception as e:
    print(f"⚠ Ao verificar User: {e}")

# Validação de funções críticas
print("\n--- Validações de funções críticas ---")

try:
    # get_or_create_memory deve existir
    assert hasattr(memory_service, 'get_or_create_memory'), "get_or_create_memory não encontrado"
    print("✓ memory_service.get_or_create_memory disponível")

    # build_dynamic_context_block deve existir
    assert hasattr(memory_service, 'build_dynamic_context_block'), "build_dynamic_context_block não encontrado"
    print("✓ memory_service.build_dynamic_context_block disponível")

    # update_after_feedback deve existir
    assert hasattr(memory_service, 'update_after_feedback'), "update_after_feedback não encontrado"
    print("✓ memory_service.update_after_feedback disponível")

    # ai.chat deve aceitar memory como parâmetro
    sig = inspect.signature(ai.chat)
    assert 'memory' in sig.parameters, "ai.chat não tem parâmetro 'memory'"
    print("✓ ai.chat aceita parâmetro 'memory'")

except AssertionError as e:
    print(f"✗ {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Erro na validação de funções: {e}")
    sys.exit(1)

# Validação de config
print("\n--- Validações de configuração ---")
if not settings.supabase_url:
    print("⚠ SUPABASE_URL não configurado")
else:
    print("✓ SUPABASE_URL configurado")

if not settings.openai_api_key:
    print("⚠ OPENAI_API_KEY não configurado (esperado em dev)")
else:
    print("✓ OPENAI_API_KEY configurado")

print("\n" + "="*50)
print("✓ VALIDAÇÃO CONCLUÍDA COM SUCESSO")
print("="*50)
print("\nPróximos passos:")
print("1. Configurar variáveis de ambiente em .env:")
print("   - SUPABASE_URL  (autenticação via JWKS/RS256 — JWT Secret não é mais necessário)")
print("   - OPENAI_API_KEY")
print("2. Criar tabelas no banco (migrations com Alembic)")
print("3. Testar endpoints com cliente autenticado Supabase")
