from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.core.config import settings


class VectorStoreService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_size = 384

    def ensure_collection_exists(self) -> None:
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def upsert_chunks(
        self,
        document_id: int,
        user_id: int,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:
        self.ensure_collection_exists()

        points = []

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = document_id * 100000 + index

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "document_id": document_id,
                        "user_id": user_id,
                        "chunk_index": index,
                        "content": chunk,
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def search_chunks(
            self,
            document_id: int,
            user_id: int,
            query_embedding: list[float],
            limit: int = 5,
    ) -> list[dict]:
        self.ensure_collection_exists()

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter={
                "must": [
                    {
                        "key": "document_id",
                        "match": {"value": document_id},
                    },
                    {
                        "key": "user_id",
                        "match": {"value": user_id},
                    },
                ]
            },
            limit=limit,
        )

        return [
            {
                "chunk_index": point.payload["chunk_index"],
                "content": point.payload["content"],
                "score": point.score,
            }
            for point in response.points
        ]

    def delete_document_vectors(
            self,
            document_id: int,
            user_id: int,
    ) -> None:
        self.ensure_collection_exists()

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    ),
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id),
                    ),
                ]
            ),
        )

    def search_user_chunks(
            self,
            user_id: int,
            query_embedding: list[float],
            limit: int = 8,
    ) -> list[dict]:
        self.ensure_collection_exists()

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter={
                "must": [
                    {
                        "key": "user_id",
                        "match": {"value": user_id},
                    },
                ]
            },
            limit=limit,
        )

        return [
            {
                "document_id": point.payload["document_id"],
                "chunk_index": point.payload["chunk_index"],
                "content": point.payload["content"],
                "score": point.score,
            }
            for point in response.points
        ]