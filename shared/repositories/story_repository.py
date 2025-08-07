from __future__ import annotations
from typing import Any, Dict

from .base_repository import BaseRepository
from ..utils.exceptions import NotFoundError


class StoryRepository(BaseRepository[Dict[str, Any]]):
    """Simple dict-based Story repository (tests用の最小実装)."""

    collection_name = "stories"

    def __init__(self, db_client):
        super().__init__(db_client, self.collection_name)

    def _to_document(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        return dict(entity)

    def _to_entity(self, document: Dict[str, Any], doc_id: str = None) -> Dict[str, Any]:
        data = dict(document)
        if doc_id is not None:
            data.setdefault("id", doc_id)
        return data

    async def create_story(self, story_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        await self.create(payload, document_id=story_id)
        return await self.get_story(story_id)

    async def get_story(self, story_id: str) -> Dict[str, Any]:
        doc = await self.get_by_id(story_id)
        if not doc:
            raise NotFoundError(f"Story {story_id} not found")
        return doc
