"""Admin management schemas."""

from pydantic import BaseModel, EmailStr, Field


class AdminOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    is_super_admin: bool

    model_config = {"from_attributes": True}


class AdminCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_super_admin: bool = False


class AdminUpdateRequest(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    is_super_admin: bool | None = None


class ProfileUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
