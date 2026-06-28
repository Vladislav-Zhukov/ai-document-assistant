from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    chunk_index: int
    content: str
    score: float


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]


class MultiDocumentSourceChunk(BaseModel):
    document_id: int
    filename: str | None = None
    chunk_index: int
    content: str
    score: float


class MultiDocumentQuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[MultiDocumentSourceChunk]