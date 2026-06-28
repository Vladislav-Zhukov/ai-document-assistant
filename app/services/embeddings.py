from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    def embed_text(self, text: str) -> list[float]:
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts)
        return [embedding.tolist() for embedding in embeddings]