from typing import List, Annotated, Optional

from pydantic import BaseModel, Field
from fastapi import UploadFile, Form, File, Query
from uuid import UUID
from datetime import datetime
from core.models.enumrators import Languages


class CreateAnnouncement:
    def __init__(
        self,
        title: str = Form(..., description="Title of the announcement"),
        description: str = Form(..., description="Description of the announcement"),
        files: List[UploadFile] | str | None = File(
            None, description="List of uploaded images", media_type="image/*"
        ),
    ):
        self.files = files
        self.title = title
        self.description = description


class GetAnnouncement(BaseModel):
    uuid: Annotated[UUID, Field(description="UUID of the announcement")]
    images: Annotated[List[str], Field(description="Announcement's images")]
    created_at: Annotated[datetime, Field(description="Created at of the announcement")]
    updated_at: Annotated[datetime, Field(description="Updated at of the announcement")]
    translations: dict[str, dict[str, str]]


class GetAnnouncementWithSelectedLanguage(BaseModel):
    uuid: Annotated[UUID, Field(description="UUID of the announcement")]
    title: str | None = None
    description: str | None = None
    images: Annotated[List[str], Field(description="Announcement's images")]
    created_at: Annotated[datetime, Field(description="Created at of the announcement")]
    updated_at: Annotated[datetime, Field(description="Updated at of the announcement")]


class DeleteAnnouncement(BaseModel):
    uuids: set[UUID]


class UpdateAnnouncement(BaseModel):
    title: Optional[str] = Field(None, min_length=5)
    description: Optional[str] = Field(None, min_length=5)
    images: List[str] | None = None


class UploadImagesToUpdateAnnouncement:
    def __init__(
        self,
        files: List[UploadFile] = File(
            ..., description="List of uploaded images", media_type="image/*"
        ),
    ):
        self.files = files
