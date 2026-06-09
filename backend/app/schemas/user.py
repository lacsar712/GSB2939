"""
用户相关 Schema
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class RoleBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class RoleResponse(RoleBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    name: str
    code: str
    type: Optional[str] = None
    parent_id: Optional[int] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    sort: Optional[int] = 0


class UserBase(BaseModel):
    username: str
    real_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role_ids: Optional[List[int]] = []


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = []


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class LoginRequest(BaseModel):
    username: str
    password: str
