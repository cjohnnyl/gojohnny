from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MessageRequest(BaseModel):
    content: str
    conversation_id: Optional[int] = None  # None = nova conversa


class MessageResponse(BaseModel):
    conversation_id: int
    message_id: int
    role: str
    content: str
    model_used: Optional[str]
    tokens_used: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
