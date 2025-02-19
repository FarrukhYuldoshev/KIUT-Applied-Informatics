from typing import List, Annotated

from pydantic import BaseModel, Field
from fastapi import UploadFile, Form, File
from uuid import UUID
from datetime import datetime


class CreateAnnouncement:
    def __init__(
        self,
        title: Annotated[str, Form(..., description="Title of the announcement")],
        description: Annotated[
            str, Form(..., description="Description of the announcement")
        ],
        files: List[UploadFile] | str | None = File(
            None, description="List of uploaded images", media_type="image/*"
        ),
    ):
        self.title = title
        self.description = description
        self.files = files


class GetAnnouncement(BaseModel):
    uuid: Annotated[UUID, Field(description="UUID of the announcement")]
    title: Annotated[str, Field(description="Title of the announcement")]
    description: Annotated[str, Field(description="Description of the announcement")]
    images: Annotated[List[str], Field(description="Announcement's images")]
    views: Annotated[int, Field(description="Announcement's views")]
    created_at: Annotated[datetime, Field(description="Created at of the announcement")]
    updated_at: Annotated[datetime, Field(description="Updated at of the announcement")]
