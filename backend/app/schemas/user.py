from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict

from app.models.user import UserRole

class UserBase(BaseModel):
    """Base User Schema with common attributes"""
    email: EmailStr
    username: str
    role: Optional[str] = "USER"
    first_name: Optional[str] = Field(None, min_length=2, max_length=50, description="First name of the user")
    last_name: Optional[str] = Field(None, min_length=2, max_length=50, description="Last name of the user")
    is_active: Optional[bool] = True
    department: Optional[str] = None
    level: Optional[int] = 1
    location: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Optional[str] = UserRole.USER.value

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    """Schema for user login"""
    email: str
    password: str

    # email required check
    @validator('email')
    def email_required(cls, v):
        """Validate email for required"""
        if not v:
            raise ValueError('Email is required')
        return v

    @validator('password')
    def password_required(cls, v):
        """Validate password for required"""
        if not v:
            raise ValueError('Password is required')
        return v

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    roles: Optional[List[str]] = []
    attributes: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator('roles', pre=True)
    def extract_role_names(cls, v):
        """Extract role names if they are Role objects"""
        if isinstance(v, list):
            return [r.name if hasattr(r, 'name') else str(r) for r in v]
        return v

    @validator('attributes', always=True)
    def set_attributes(cls, v, values):
        """Map flat user fields to attributes object for frontend compatibility"""
        return {
            "department": values.get("department") or "General",
            "level": values.get("level") or 1,
            "location": values.get("location") or "Main Office"
        }

    # Pydantic v2: allow constructing from ORM objects/attributes
    model_config = ConfigDict(from_attributes=True)