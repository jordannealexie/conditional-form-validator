from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    user_role = Column(String, nullable=True)  # Primary role name
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=True)
    active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    
    # Attributes for ABAC
    department = Column(String, nullable=True)
    level = Column(Integer, default=1)
    location = Column(String, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_onupdate=func.now())
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment="User ID who last updated this record")
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    bank = relationship("Bank", back_populates="bank_users")
    abac_attributes = relationship("UserAttribute", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    



class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    permissions = Column(JSON, nullable=True)  # JSONB permissions as per spec
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment="User ID of creator")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment="User ID of last updater")
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")

class RefreshToken(Base):
    """Model for managing refresh tokens and revocation"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class ResourceRelationship(Base):
    """For ReBAC - defines relationships between subjects (users/roles) and resources"""
    __tablename__ = "resource_relationships"

    id = Column(Integer, primary_key=True, index=True)
    # Subject of the relationship (who/what has the relationship)
    subject_type = Column(String, nullable=False)  # "user", "role", "resource"
    subject_id = Column(String, nullable=False)    # username, role name, or resource identifier
    # Target resource
    resource_type = Column(String, nullable=False)  # e.g., "document", "project"
    resource_id = Column(String, nullable=False)    # e.g., "doc_123", "proj_456"
    # Relationship type
    parent_resource_type = Column(String, nullable=False)  # parent resource type (kept for backward compatibility)
    parent_resource_id = Column(String, nullable=False)    # parent resource id (kept for backward compatibility)
    relationship_type = Column(String, nullable=False)     # e.g., "owner_of", "member_of", "parent_of", "manages"
    created_at = Column(DateTime(timezone=True), server_default=func.now())