from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.conversation import Conversation, Message
from ..models.user import User
from ..schemas.chat import ConversationResponse, MessageRequest, MessageResponse
from ..services import ai
from ..services.deps import get_current_user

router = APIRouter()

# Número máximo de mensagens do histórico enviadas para Claude
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
def send_message(
    body: MessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = _get_or_create_conversation(db, current_user.id, body.conversation_id)

    # Persiste mensagem do usuário
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=body.content,
    )
    db.add(user_msg)
    db.flush()

    # Monta histórico para enviar à Claude (últimas N mensagens, excluindo a que acabamos de adicionar)
    history = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id, Message.id != user_msg.id)
        .order_by(Message.created_at.desc())
        .limit(_HISTORY_LIMIT)
        .all()
    )
    history_messages = [{"role": m.role, "content": m.content} for m in reversed(history)]
    history_messages.append({"role": "user", "content": body.content})

    # Chama Claude
    profile = current_user.profile
    reply, tokens = ai.chat(history_messages, profile=profile)

    # Persiste resposta do assistente
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=reply,
        tokens_used=tokens,
        model_used=ai.settings.anthropic_model_chat,
    )
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
