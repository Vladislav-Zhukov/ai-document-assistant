from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.message import MessageRole
from app.models.user import User
from app.repositories.chat import ChatRepository
from app.repositories.document import DocumentRepository
from app.repositories.message import MessageRepository
from app.schemas.chat import ChatCreate, ChatRead
from app.schemas.message import ChatAskResponse, MessageCreate, MessageRead
from app.services.embeddings import EmbeddingService
from app.services.llm import OpenRouterProvider
from app.services.rate_limit import check_rate_limit
from app.services.vector_store import VectorStoreService
from fastapi.responses import StreamingResponse
from app.models.document import DocumentStatus

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id_and_user(
        document_id=chat_data.document_id,
        user_id=current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    chat_repo = ChatRepository(db)
    return await chat_repo.create(
        user_id=current_user.id,
        document_id=document.id,
        title=chat_data.title,
    )


@router.get("", response_model=list[ChatRead])
async def list_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    return await chat_repo.list_by_user(current_user.id)


@router.get("/{chat_id}/messages", response_model=list[MessageRead])
async def list_chat_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    chat = await chat_repo.get_by_id_and_user(
        chat_id=chat_id,
        user_id=current_user.id,
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    message_repo = MessageRepository(db)
    return await message_repo.list_by_chat(chat_id=chat.id)


@router.post("/{chat_id}/messages", response_model=ChatAskResponse)
async def ask_in_chat(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_rate_limit(
        user_id=current_user.id,
        action="chat_message",
    )

    chat_repo = ChatRepository(db)
    chat = await chat_repo.get_by_id_and_user(
        chat_id=chat_id,
        user_id=current_user.id,
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id_and_user(
        document_id=chat.document_id,
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

    message_repo = MessageRepository(db)

    user_message = await message_repo.create(
        chat_id=chat.id,
        role=MessageRole.USER,
        content=message_data.content,
    )

    messages = await message_repo.list_by_chat(chat_id=chat.id)

    chat_history = [
        {
            "role": message.role.value,
            "content": message.content,
        }
        for message in messages[:-1]
    ]

    embedding_service = EmbeddingService()
    question_embedding = embedding_service.embed_text(message_data.content)

    vector_store = VectorStoreService()
    results = vector_store.search_chunks(
        document_id=document.id,
        user_id=current_user.id,
        query_embedding=question_embedding,
        limit=settings.TOP_K_RESULTS,
    )

    llm_provider = OpenRouterProvider()
    answer = await llm_provider.generate_answer(
        question=message_data.content,
        context_chunks=[result["content"] for result in results],
        chat_history=chat_history,
    )

    assistant_message = await message_repo.create(
        chat_id=chat.id,
        role=MessageRole.ASSISTANT,
        content=answer,
    )

    return ChatAskResponse(
        user_message=user_message,
        assistant_message=assistant_message,
    )


@router.post("/{chat_id}/stream")
async def stream_chat_answer(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    chat = await chat_repo.get_by_id_and_user(
        chat_id=chat_id,
        user_id=current_user.id,
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id_and_user(
        document_id=chat.document_id,
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

    message_repo = MessageRepository(db)

    user_message = await message_repo.create(
        chat_id=chat.id,
        role=MessageRole.USER,
        content=message_data.content,
    )

    messages = await message_repo.list_by_chat(chat_id=chat.id)

    chat_history = [
        {
            "role": message.role.value,
            "content": message.content,
        }
        for message in messages[:-1]
    ]

    embedding_service = EmbeddingService()
    question_embedding = embedding_service.embed_text(message_data.content)

    vector_store = VectorStoreService()
    results = vector_store.search_chunks(
        document_id=document.id,
        user_id=current_user.id,
        query_embedding=question_embedding,
        limit=settings.TOP_K_RESULTS,
    )

    llm_provider = OpenRouterProvider()

    async def event_generator():
        full_answer = ""

        async for token in llm_provider.stream_answer(
            question=message_data.content,
            context_chunks=[result["content"] for result in results],
            chat_history=chat_history,
        ):
            full_answer += token
            yield f"data: {token}\n\n"

        await message_repo.create(
            chat_id=chat.id,
            role=MessageRole.ASSISTANT,
            content=full_answer,
        )

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )