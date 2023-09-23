from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional, List


class Data:
    def __init__(self, custom_item_number: float):
        self.custom_item_number = custom_item_number


class UserSchema(BaseModel):
    email: EmailStr = Field(..., description="user email")
    password: str = Field(..., min_length=5, max_length=24, description="user password")


class UpdateUser(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class MeetingData(BaseModel):
    meeting_name: str
    date_of_activity: str


class UpdateMeeting(BaseModel):
    meeting_id: str
    meeting_name: str = None
    date_of_activity: str = None


class ParticipantData(BaseModel):
    meeting_id: str
    user_ids: list[str]


class MeetingIds(BaseModel):
    meeting_ids: list[str]


class FeedbackId(BaseModel):
    feedback_id: str


class FeedbackData(BaseModel):
    meeting_id: str
    feedback_text: str


class UpdateFeedback(BaseModel):
    feedback_id: str
    feedback_text: str


class CheckData(BaseModel):
    meeting_id: str
    custom_item_number: float
    participant_ids: Optional[List[str]] = None


class ItemData(BaseModel):
    item_name: str
    price: float


class PurchaseData(BaseModel):
    meeting_id: str
    custom_item_id: str


class UpdateItem(BaseModel):
    item_name: str = None
    price: float = None
    custom_item_number: float = None


class RemoveFromCheckData(BaseModel):
    meeting_id: str
    custom_item_id: str
    participant_ids: List[str]

