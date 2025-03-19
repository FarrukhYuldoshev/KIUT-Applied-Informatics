from typing import List, Annotated

from pydantic import BaseModel, ConfigDict, Field


class TeachersImage(BaseModel):
    image: str
    model_config = ConfigDict(from_attributes=True)


class Index(BaseModel):
    teachers: Annotated[List[TeachersImage], Field(..., description="Teachers image")]
    count: int = Field(..., description="Number of teachers")
