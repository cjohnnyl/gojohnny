from typing import Optional
from openai import APIError, BadRequestError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..main import limiter, _get_user_id_from_token
from ..models.conversation import Conversation, Message
from ..models.user import User
from ..schemas.chat import ConversationResponse, MessageRequest, MessageResponse
from ..services import ai
from ..services.deps import get_current_user

router = APIRouter()

# Número máximo de mensagens do histórico enviadas para a IA
_HISTORY_LIMIT = 20


def _get_or_create_conversation(db: Session, user_id: int, conversation_id: Optional[int]) -> Conversation:
    if conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        ).first()
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")
        return conv

    conv = Conversation(user_id=user_id)
    db.add(conv)
    db.flush()
    return conv


@router.post("/message", response_model=MessageResponse)
async def send_message(
    request: Request,
    body: MessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = _get_or_create_conversation(db, current_user.id, body.conversation_id)

    # Busca histórico ANTES de qualquer escrita (conversa já existente)
    history = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at.desc())
        .limit(_HISTORY_LIMIT)
        .all()
    )
    history_messages = [{"role": m.role, "content": m.content} for m in reversed(history)]
    history_messages.append({"role": "user", "content": body.content})

    # Chama a IA ANTES de escrever qualquer mensagem no banco
    profile = current_user.profile
    try:
        reply, tokens = ai.chat(history_messages, profile=profile)
    except BadRequestError as e:
        logger.error(f"OpenAI {type(e).__name__} (status={getattr(e, 'status_code', 'N/A')})")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Saldo insuficiente ou requisição inválida. Verifique sua conta OpenAI.",
        )
    except APIError as e:
        logger.error(f"OpenAI {type(e).__name__} (status={getattr(e, 'status_code', 'N/A')})")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Erro ao se comunicar com o modelo de IA. Tente novamente.",
        )

    # Persiste user + assistant em uma única transação (atômica)
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=body.content,
    )
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=reply,
        tokens_used=tokens,
        model_used=ai.settings.openai_model_chat,
    )
    db.add(user_msg)
    db.add(assistant_msg)

    # Gera título automático na primeira troca
    if not conv.title:
        conv.title = body.content[:80]

    db.commit()
    db.refresh(assistant_msg)

    return MessageResponse(
        conversation_id=conv.id,
        message_id=assistant_msg.id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        model_used=assistant_msg.model_used,
        tokens_used=assistant_msg.tokens_used,
        created_at=assistant_msg.created_at,
    )


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at}
        for m in conv.messages
    ]
