from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base_class import Base

class AuditLog(Base):
    """Audit log model for tracking all sensitive user actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String, nullable=True, index=True)
    action = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=False, index=True, server_default="system")
    resource_id = Column(String, nullable=True, index=True)
    status = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    payload = Column(JSON, nullable=True)
    details = Column(JSON, nullable=True) # Spec says JSONB
    
    # Change tracking fields
    changes = Column(JSON, nullable=True, comment="Before and after values in JSON format")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User ID who created this record")
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User ID who updated this record")
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User ID who deleted this record")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
