from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    document_id: int
    title: str = "New chat"


class ChatRead(BaseModel):
    id: int
    user_id: int
    document_id: int
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)