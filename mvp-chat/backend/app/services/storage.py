"""Abstracción de almacenamiento: local (actual) y S3 (futuro)."""

import uuid
from pathlib import Path

from app.core.config import settings

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


class StorageBackend:
    """Protocolo de backend de storage."""

    def save(self, file_content: bytes, filename: str, subdir: str = "avatars") -> str:
        """Guarda el archivo y retorna la URL pública."""
        raise NotImplementedError

    def delete(self, url_or_path: str) -> None:
        """Elimina un archivo si existe."""
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    """Guarda archivos en disco local. URLs relativas para servir con StaticFiles."""

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.url_prefix = settings.static_url_prefix

    def save(self, file_content: bytes, filename: str, subdir: str = "avatars") -> str:
        dir_path = self.upload_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)

        ext = Path(filename).suffix.lower().lstrip(".")
        if ext not in ALLOWED_EXTENSIONS:
            ext = "jpg"

        unique_name = f"{uuid.uuid4().hex}.{ext}"
        file_path = dir_path / unique_name
        file_path.write_bytes(file_content)

        return f"{self.url_prefix}/{subdir}/{unique_name}"

    def delete(self, url_or_path: str) -> None:
        if not url_or_path or not url_or_path.startswith(f"{self.url_prefix}/"):
            return
        rel = url_or_path[len(self.url_prefix) + 1 :]
        file_path = self.upload_dir / rel
        if file_path.exists() and file_path.is_file():
            file_path.unlink(missing_ok=True)


class S3StorageBackend(StorageBackend):
    """Backend para S3. Implementar cuando se migre."""

    def save(self, file_content: bytes, filename: str, subdir: str = "avatars") -> str:
        raise NotImplementedError(
            "S3StorageBackend: configurar S3_BUCKET, S3_REGION, etc. "
            "y completar implementación con boto3."
        )

    def delete(self, url_or_path: str) -> None:
        raise NotImplementedError("S3StorageBackend: implementar delete con boto3.")


def get_storage() -> StorageBackend:
    """Factory: retorna el backend según STORAGE_BACKEND."""
    if settings.storage_backend == "s3":
        return S3StorageBackend()
    return LocalStorageBackend()
