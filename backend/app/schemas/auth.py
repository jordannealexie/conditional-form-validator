from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

# Valid locations - EXACTLY 17 cities as specified
VALID_LOCATIONS = [
    "Makati", "Quezon City", "Paranaque", "Pampanga", "Bulacan",
    "Cavite", "Laguna", "Batangas", "Cebu", "Iloilo", "Bacolod",
    "Davao", "Cagayan De Oro", "Pagadian", "Tagum", "Zamboanga", "General Santos"
]

# Valid levels - only 1, 2, 3
VALID_LEVELS = [1, 2, 3]


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    user_role: Optional[str] = None
    bank_id: Optional[int] = None
    permissions: Optional[list] = None


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    user_role: Optional[str] = "fieldman"
    is_superuser: Optional[bool] = False
    bank_id: Optional[int] = None
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    full_name: Optional[str] = None
    department: Optional[str] = None
    level: int = Field(1, ge=1, le=3, description="User level (1-3 only)")
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


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    user_role: Optional[str] = None
    bank_id: Optional[int] = None
    active: bool
    is_superuser: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    level: int
    location: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserAdminUpdate(BaseModel):
    """Schema for admin updating user (email, role, bank, active, department, location)"""
    email: Optional[EmailStr] = None
    user_role: Optional[str] = None
    bank_id: Optional[int] = None
    active: Optional[bool] = None
    department: Optional[str] = None
    location: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
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


class RefreshRequest(BaseModel):
    refresh_token: str