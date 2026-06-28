from uuid import uuid4

from fastapi import UploadFile
from minio import Minio

from app.core.config import settings


class StorageService:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    def ensure_bucket_exists(self) -> None:
        exists = self.client.bucket_exists(self.bucket_name)
        if not exists:
            self.client.make_bucket(self.bucket_name)

    def upload_file(self, file: UploadFile, user_id: int) -> str:
        self.ensure_bucket_exists()

        file_extension = file.filename.split(".")[-1]
        object_name = f"users/{user_id}/{uuid4()}.{file_extension}"

        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=file.content_type,
        )

        return object_name

    def download_file(self, object_name: str) -> bytes:
        response = self.client.get_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
        )

        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete_file(self, object_name: str) -> None:
        self.client.remove_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
        )