from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict

from app.models.user import UserRole

# Valid locations - EXACTLY 17 cities as specified
VALID_LOCATIONS = [
    "Makati", "Quezon City", "Paranaque", "Pampanga", "Bulacan",
    "Cavite", "Laguna", "Batangas", "Cebu", "Iloilo", "Bacolod",
    "Davao", "Cagayan De Oro", "Pagadian", "Tagum", "Zamboanga", "General Santos"
]

# Valid levels - only 1, 2, 3
VALID_LEVELS = [1, 2, 3]


class UserBase(BaseModel):
    """Base User Schema with common attributes"""
    email: EmailStr
    username: str
    role: Optional[str] = "USER"
    first_name: Optional[str] = Field(None, min_length=2, max_length=50, description="First name of the user")
    last_name: Optional[str] = Field(None, min_length=2, max_length=50, description="Last name of the user")
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    department: Optional[str] = None
    level: Optional[int] = Field(1, ge=1, le=3, description="User level (1-3 only)")
    location: Optional[str] = None

    @validator('level')
    def validate_level(cls, v):
        """Validate level is 1, 2, or 3"""
        if v is not None and v not in VALID_LEVELS:
            raise ValueError(f'Level must be one of {VALID_LEVELS}')
        return v

    @validator('location')
    def validate_location(cls, v):
        """Validate location is from the allowed list"""
        if v is not None and v not in VALID_LOCATIONS:
            raise ValueError(f'Location must be one of: {", ".join(VALID_LOCATIONS)}')
        return v

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
    department: Optional[str] = None
    location: Optional[str] = None
    level: Optional[int] = Field(None, ge=1, le=3, description="User level (1-3 only)")

    @validator('level')
    def validate_level(cls, v):
        """Validate level is 1, 2, or 3"""
        if v is not None and v not in VALID_LEVELS:
            raise ValueError(f'Level must be one of {VALID_LEVELS}')
        return v

    @validator('location')
    def validate_location(cls, v):
        """Validate location is from the allowed list"""
        if v is not None and v not in VALID_LOCATIONS:
            raise ValueError(f'Location must be one of: {", ".join(VALID_LOCATIONS)}')
        return v

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
    updated_by: Optional[int] = None  # Audit field: user ID who last updated this user

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