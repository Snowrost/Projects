import uuid
import re
from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from enum import Enum as PythonEnum

from src.core.db import Base
from src.core.db.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(55))
    lastname = Column(String(120))
    password = Column(String(255))
    email = Column(String(150), unique=True)
    user_status = Column(String(25), default="new")

# Relationships
    participants = relationship("Participant", back_populates="user")
    owned_meetings = relationship("Meeting", back_populates="owner")
    feedbacks = relationship("Feedback", back_populates="user")

    @validates("email")
    def validate_email(self, key, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")
        return email
