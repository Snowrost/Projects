from sqlalchemy import Column, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from src.core.db.mixins import TimestampMixin
from src.core.db import Base



class Check(Base, TimestampMixin):
    __tablename__ = 'checks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    participant_id = Column(UUID(as_uuid=True), ForeignKey('participants.id'))
    custom_item_id = Column(UUID(as_uuid=True), ForeignKey('custom_items.id'))
    custom_item_number = Column(Float)
    splited_bill = Column(Float)

    # Relationships
    participant = relationship("Participant", back_populates="checks")
    custom_item = relationship("CustomItem", back_populates="checks")

