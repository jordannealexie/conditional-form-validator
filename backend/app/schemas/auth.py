from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

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
    bank_id: Optional[int] = None
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    full_name: Optional[str] = None
    department: Optional[str] = None
    level: int = 1
    location: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    user_role: Optional[str] = None
    bank_id: Optional[int] = None
    active: bool
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
    """Schema for admin updating user (email, role, bank, active)"""
    email: Optional[EmailStr] = None
    user_role: Optional[str] = None
    bank_id: Optional[int] = None
    active: Optional[bool] = None


class RefreshRequest(BaseModel):
    refresh_token: str