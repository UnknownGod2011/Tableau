"""
Base model classes and common fields
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class UUIDMixin:
    """Mixin for UUID primary keys"""
    
    @declared_attr
    def id(cls):
        return Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class AuditMixin:
    """Mixin for audit trail fields"""
    
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    audit_notes = Column(Text, nullable=True)


class BaseModel(Base, UUIDMixin, TimestampMixin, AuditMixin):
    """Base model with common fields"""
    
    __abstract__ = True
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }