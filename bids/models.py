from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class BidStatus(str, Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CANCELED = "Canceled"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class NewRequest(BaseModel):
    name: str
    description: str
    tenderId: UUID


class PatchRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[BidStatus] = None
