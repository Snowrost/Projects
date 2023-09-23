import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.db.mixins import TimestampMixin
from src.core.db import Base


class Meeting(Base, TimestampMixin):
    __tablename__ = 'meetings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_name = Column(String(55))
    date_of_activity = Column(DateTime(timezone=True))
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

# Relationships
    owner = relationship("User", back_populates="owned_meetings")
    participants = relationship("Participant", back_populates="meeting")
    feedbacks = relationship("Feedback", back_populates="meeting")

