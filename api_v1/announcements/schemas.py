from typing import List, Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict
from fastapi import UploadFile, Form, File, Query
from uuid import UUID
from datetime import datetime
from core.models.enumrators import Languages


class PaginationParams(BaseModel):
    total: Annotated[int, Field(..., ge=0)]
    count: Annotated[int, Field(..., ge=1)]
    pagination: Annotated[dict[str, str | None], Field(...)]


class CreateAnnouncement:
    def __init__(
        self,
        title: str = Form(..., description="Title of the announcement"),
        description: str = Form(..., description="Description of the announcement"),
        files: List[UploadFile] | str | None = File(
            None, description="List of uploaded images"
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
    title: str | None = None
    description: str | None = None
    translations: dict[str, dict[str, str]] | None = None
    model_config = ConfigDict(from_attributes=True)


class AnnouncementsResponse(BaseModel):
    data: List[GetAnnouncement] = Field(..., description="Data of the announcement")
    pagination_params: (
        Annotated[
            PaginationParams,
            Field(None, description="Pagination details of the announcement"),
        ]
        | None
    ) = None


class DeleteAnnouncement(BaseModel):
    uuids: set[UUID]


class UpdateDetails(BaseModel):
    title: str = Field(min_length=5)
    description: str = Field(min_length=5)


class UpdateAnnouncement(BaseModel):
    images: List[str] | None = Field(
        None, description="Announcement's images", min_length=1
    )
    translations: dict[Languages, UpdateDetails] | None = Field(
        default=None,
        example={
            lang.value: {"title": "text", "description": "text"} for lang in Languages
        },
        description=f"Allowed keys: {[lang.value for lang in Languages]}",
        min_length=1,
    )


class UploadImagesToUpdateAnnouncement:
    def __init__(
        self,
        files: List[UploadFile] = File(
            ..., description="List of uploaded images", media_type="image/*"
        ),
    ):
        self.files = files
