from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.message import MessageRole


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: int
    chat_id: int
    role: MessageRole
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatAskResponse(BaseModel):
    user_message: MessageRead
    assistant_message: MessageRead