from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rate_limit import check_rate_limit
from app.core.config import settings
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentRead, DocumentSummaryResponse
from app.services.storage import StorageService
from app.services.document_parser import DocumentParser
from app.services.chunking import TextChunker
from app.repositories.document_chunk import DocumentChunkRepository
from app.schemas.document_chunk import DocumentChunkRead
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.llm import OpenRouterProvider
from app.models.document import DocumentStatus
from app.services.task_queue import document_queue
from app.workers.tasks import process_document
from app.schemas.question import (
    QuestionRequest,
    QuestionResponse,
    SourceChunk,
    MultiDocumentQuestionResponse,
    MultiDocumentSourceChunk,
)


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    storage_service = StorageService()
    storage_path = storage_service.upload_file(file=file, user_id=current_user.id)

    document_repo = DocumentRepository(db)
    document = await document_repo.create(
        user_id=current_user.id,
        filename=file.filename,
        content_type=file.content_type,
        storage_path=storage_path,
        status=DocumentStatus.PROCESSING,
    )

    document_queue.enqueue(
        process_document,
        document.id,
    )

    return document


@router.get("", response_model=list[DocumentRead])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document_repo = DocumentRepository(db)
    return await document_repo.list_by_user(current_user.id)


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkRead])
async def get_document_chunks(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id_and_user(
        document_id=document_id,
        user_id=current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    chunk_repo = DocumentChunkRepository(db)
    return await chunk_repo.list_by_document(document_id=document.id)


@router.post("/{document_id}/ask", response_model=QuestionResponse)
async def ask_document(
    document_id: int,
    question_data: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_rate_limit(
        user_id=current_user.id,
        action="ask_document",
    )

    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id_and_user(
        document_id=document_id,
        user_id=current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.status != DocumentStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document is not ready yet. Current status: {document.status.value}",
        )

    embedding_service = EmbeddingService()
    question_embedding = embedding_service.embed_text(question_data.question)

    vector_store = VectorStoreService()
    results = vector_store.search_chunks(
        document_id=document.id,
        user_id=current_user.id,
        query_embedding=question_embedding,
        limit=settings.TOP_K_RESULTS,
    )

    llm_provider = OpenRouterProvider()

    answer = await llm_provider.generate_answer(
        question=question_data.question,
        context_chunks=[result["content"] for result in results],
    )

    return QuestionResponse(
        question=question_data.question,
        answer=answer,
        sources=[
            SourceChunk(
                chunk_index=result["chunk_index"],
                content=result["content"],
                score=result["score"],
            )
            for result in results
        ],
    )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id_and_user(
        document_id=document_id,
        user_id=current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    storage_service = StorageService()
    storage_service.delete_file(document.storage_path)

    vector_store = VectorStoreService()
    vector_store.delete_document_vectors(
        document_id=document.id,
        user_id=current_user.id,
    )

    await document_repo.delete(document)

    return None

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id_and_user(
        document_id=document_id,
        user_id=current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    storage_service = StorageService()
    storage_service.delete_file(document.storage_path)

    vector_store = VectorStoreService()
    vector_store.delete_document_vectors(
        document_id=document.id,
        user_id=current_user.id,
    )

    await document_repo.delete(document)

    return None


@router.post("/ask", response_model=MultiDocumentQuestionResponse)
async def ask_all_documents(
    question_data: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document_repo = DocumentRepository(db)
    ready_documents = await document_repo.get_ready_documents_by_user(
        user_id=current_user.id,
    )

    if not ready_documents:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You don't have ready documents yet",
        )

    documents_by_id = {
        document.id: document
        for document in ready_documents
    }

    embedding_service = EmbeddingService()
    question_embedding = embedding_service.embed_text(question_data.question)

    vector_store = VectorStoreService()
    results = vector_store.search_user_chunks(
        user_id=current_user.id,
        query_embedding=question_embedding,
        limit=settings.TOP_K_RESULTS,
    )

    chunk_repo = DocumentChunkRepository(db)

    keyword_chunks = await chunk_repo.keyword_search_by_user(
        user_id=current_user.id,
        query=question_data.question,
        limit=settings.TOP_K_RESULTS,
    )

    results = [
        result for result in results
        if result["document_id"] in documents_by_id
    ]

    vector_context = [
        result["content"]
        for result in results
    ]

    keyword_context = [
        chunk.content
        for chunk in keyword_chunks
    ]

    combined_context = list(dict.fromkeys(vector_context + keyword_context))


    llm_provider = OpenRouterProvider()
    answer = await llm_provider.generate_answer(
        question=question_data.question,
        context_chunks=combined_context,
    )

    return MultiDocumentQuestionResponse(
        question=question_data.question,
        answer=answer,
        sources=[
            MultiDocumentSourceChunk(
                document_id=result["document_id"],
                filename=documents_by_id[result["document_id"]].filename,
                chunk_index=result["chunk_index"],
                content=result["content"],
                score=result["score"],
            )
            for result in results
        ],
    )


@router.post("/{document_id}/summary", response_model=DocumentSummaryResponse)
async def summarize_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_rate_limit(
        user_id=current_user.id,
        action="summary",
    )

    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id_and_user(
        document_id=document_id,
        user_id=current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.status != DocumentStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document is not ready yet. Current status: {document.status.value}",
        )

    chunk_repo = DocumentChunkRepository(db)
    chunks = await chunk_repo.list_by_document(document_id=document.id)

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document chunks not found",
        )

    llm_provider = OpenRouterProvider()
    summary = await llm_provider.generate_summary(
        context_chunks=[chunk.content for chunk in chunks[:10]],
    )

    return DocumentSummaryResponse(
        document_id=document.id,
        filename=document.filename,
        summary=summary,
    )