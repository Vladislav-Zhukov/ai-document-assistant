from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk
from app.models.document import Document


class DocumentChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(
        self,
        document_id: int,
        chunks: list[str],
    ) -> list[DocumentChunk]:
        chunk_objects = [
            DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                content=content,
            )
            for index, content in enumerate(chunks)
        ]

        self.db.add_all(chunk_objects)
        await self.db.commit()

        return chunk_objects

    async def list_by_document(self, document_id: int) -> list[DocumentChunk]:
        result = await self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def keyword_search_by_user(
            self,
            user_id: int,
            query: str,
            limit: int = 5,
    ) -> list[DocumentChunk]:
        result = await self.db.execute(
            select(DocumentChunk)
            .join(DocumentChunk.document)
            .where(Document.user_id == user_id)
            .where(
                func.to_tsvector("english", DocumentChunk.content).match(query)
            )
            .limit(limit)
        )

        return list(result.scalars().all())