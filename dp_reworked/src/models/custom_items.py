from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.core.db.mixins import TimestampMixin
from src.core.db import Base
from sqlalchemy.orm import relationship

class CustomItem(Base, TimestampMixin):
    __tablename__ = 'custom_items'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_name = Column(String(255))
    price = Column(Float)

    checks = relationship("Check", back_populates="custom_item")

