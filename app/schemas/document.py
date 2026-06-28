from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentRead(BaseModel):
    id: int
    filename: str
    content_type: str
    storage_path: str
    status: DocumentStatus
    created_at: datetime
    pages_count: int | None = None
    words_count: int | None = None
    chunks_count: int | None = None
    language: str | None = None
    document_type: str | None = None
    document_type_confidence: float | None = None

    model_config = ConfigDict(from_attributes=True)


class DocumentSummaryResponse(BaseModel):
    document_id: int
    filename: str
    summary: str