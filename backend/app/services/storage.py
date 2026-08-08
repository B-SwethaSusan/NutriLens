import asyncio
import logging
from pathlib import Path

from app.config import get_settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self.settings = get_settings()
        self.local_root = Path(__file__).resolve().parents[2] / "storage"
        self.local_root.mkdir(parents=True, exist_ok=True)
        self.client = None
        if self.settings.supabase_url and (self.settings.supabase_service_key or self.settings.supabase_key):
            try:
                from supabase import create_client

                self.client = create_client(self.settings.supabase_url, self.settings.supabase_service_key or self.settings.supabase_key)
            except Exception as exc:
                logger.warning("Supabase storage unavailable; using local storage: %s", exc)

    @property
    def is_remote(self) -> bool:
        return self.client is not None

    async def upload(self, path: str, content: bytes, content_type: str = "application/pdf") -> str:
        if self.client:
            await asyncio.to_thread(
                lambda: self.client.storage.from_(self.settings.supabase_storage_bucket).upload(
                    path, content, {"content-type": content_type, "upsert": "true"}
                )
            )
            return path
        target = self.local_root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(target.write_bytes, content)
        return str(target)

    async def download(self, path: str) -> bytes:
        if self.client:
            return await asyncio.to_thread(lambda: self.client.storage.from_(self.settings.supabase_storage_bucket).download(path))
        target = Path(path)
        if not target.is_absolute():
            target = self.local_root / target
        return await asyncio.to_thread(target.read_bytes)

    async def delete(self, path: str) -> None:
        if self.client:
            await asyncio.to_thread(lambda: self.client.storage.from_(self.settings.supabase_storage_bucket).remove([path]))
        else:
            target = Path(path)
            if not target.is_absolute():
                target = self.local_root / target
            if target.exists():
                await asyncio.to_thread(target.unlink)


storage_service = StorageService()
