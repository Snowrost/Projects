from sqlalchemy import Column, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

import uuid
from sqlalchemy.orm import relationship
from src.core.db.mixins import TimestampMixin
from src.core.db import Base


class Feedback(Base, TimestampMixin):
    __tablename__ = 'feedback'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey('meetings.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    comment = Column(Text)

    user = relationship("User", back_populates="feedbacks")
    meeting = relationship("Meeting", back_populates="feedbacks")

    __table_args__ = (UniqueConstraint('user_id', 'meeting_id', name='_user_meeting_uc'),)
