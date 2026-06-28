from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        document_id: int,
        title: str,
    ) -> Chat:
        chat = Chat(
            user_id=user_id,
            document_id=document_id,
            title=title,
        )
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def list_by_user(self, user_id: int) -> list[Chat]:
        result = await self.db.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        chat_id: int,
        user_id: int,
    ) -> Chat | None:
        result = await self.db.execute(
            select(Chat).where(
                Chat.id == chat_id,
                Chat.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()