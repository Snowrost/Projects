from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

import uuid
from src.core.db.mixins import TimestampMixin
from src.core.db import Base


class Participant(Base, TimestampMixin):
    __tablename__ = 'participants'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey('meetings.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="participants")
    checks = relationship("Check", back_populates="participant")