import asyncio

from app.core.database import AsyncSessionLocal
from app.models.document import DocumentStatus
from app.repositories.document import DocumentRepository
from app.repositories.document_chunk import DocumentChunkRepository
from app.services.chunking import TextChunker
from app.services.document_parser import DocumentParser
from app.services.embeddings import EmbeddingService
from app.services.storage import StorageService
from app.services.vector_store import VectorStoreService
from app.services.document_classifier import DocumentClassifierService


def process_document(document_id: int) -> None:
    asyncio.run(_process_document(document_id))


async def _process_document(document_id: int) -> None:
    async with AsyncSessionLocal() as db:
        document_repo = DocumentRepository(db)
        document = await document_repo.get_by_id(document_id)

        if document is None:
            return

        try:
            await document_repo.update_status(
                document_id=document.id,
                status=DocumentStatus.PROCESSING,
            )

            storage_service = StorageService()
            file_bytes = storage_service.download_file(document.storage_path)

            parser = DocumentParser()
            text = parser.parse(
                file_bytes=file_bytes,
                filename=document.filename,
            )

            classifier = DocumentClassifierService()
            document_type, confidence = await classifier.classify(text)

            await document_repo.update_classification(
                document_id=document.id,
                document_type=document_type,
                document_type_confidence=confidence,
            )

            chunker = TextChunker()
            chunks = chunker.split_text(text)

            words_count = len(text.split())
            chunks_count = len(chunks)
            pages_count = None
            language = None

            await document_repo.update_metadata(
                document_id=document.id,
                pages_count=pages_count,
                words_count=words_count,
                chunks_count=chunks_count,
                language=language,
            )

            chunk_repo = DocumentChunkRepository(db)
            await chunk_repo.create_many(
                document_id=document.id,
                chunks=chunks,
            )

            embedding_service = EmbeddingService()
            embeddings = embedding_service.embed_many(chunks)

            vector_store = VectorStoreService()
            vector_store.upsert_chunks(
                document_id=document.id,
                user_id=document.user_id,
                chunks=chunks,
                embeddings=embeddings,
            )

            await document_repo.update_status(
                document_id=document.id,
                status=DocumentStatus.READY,
            )

        except Exception as error:
            print(f"Document processing failed: {error}")

            await document_repo.update_status(
                document_id=document.id,
                status=DocumentStatus.FAILED,
            )