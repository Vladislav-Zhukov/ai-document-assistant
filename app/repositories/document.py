from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
            self,
            user_id: int,
            filename: str,
            content_type: str,
            storage_path: str,
            status: DocumentStatus = DocumentStatus.PROCESSING,
    ) -> Document:
        document = Document(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            storage_path=storage_path,
            status=status,
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def list_by_user(self, user_id: int) -> list[Document]:
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(
            self,
            document_id: int,
            user_id: int,
    ) -> Document | None:
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, document_id: int) -> Document | None:
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
            self,
            document_id: int,
            status: DocumentStatus,
    ) -> Document | None:
        document = await self.get_by_id(document_id)

        if document is None:
            return None

        document.status = status
        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def delete(self, document: Document) -> None:
        await self.db.delete(document)
        await self.db.commit()

    async def get_ready_documents_by_user(
            self,
            user_id: int,
    ) -> list[Document]:
        result = await self.db.execute(
            select(Document).where(
                Document.user_id == user_id,
                Document.status == DocumentStatus.READY,
            )
        )
        return list(result.scalars().all())

    async def update_metadata(
            self,
            document_id: int,
            pages_count: int | None,
            words_count: int,
            chunks_count: int,
            language: str | None = None,
    ) -> Document | None:
        document = await self.get_by_id(document_id)

        if document is None:
            return None

        document.pages_count = pages_count
        document.words_count = words_count
        document.chunks_count = chunks_count
        document.language = language

        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def update_classification(
            self,
            document_id: int,
            document_type: str,
            document_type_confidence: float,
    ) -> Document | None:
        document = await self.get_by_id(document_id)

        if document is None:
            return None

        document.document_type = document_type
        document.document_type_confidence = document_type_confidence

        await self.db.commit()
        await self.db.refresh(document)

        return document