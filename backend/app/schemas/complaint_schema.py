from pydantic import BaseModel
from typing import Optional


class ComplaintCreate(BaseModel):
    title: str
    description: str
    location: str
    city: str
    state: str
    pin_code: str
    contact_number: str


class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    department: Optional[str]
    urgency: Optional[str]
    sentiment: Optional[str]
    status: str

    class Config:
        from_attributes = True
