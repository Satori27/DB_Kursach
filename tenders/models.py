from typing import Optional
from pydantic import BaseModel
from enum import Enum


class TenderStatus(str, Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CLOSED = "Closed"

class NewRequest(BaseModel):
    name: str
    description: str


class PatchRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TenderStatus] = None

