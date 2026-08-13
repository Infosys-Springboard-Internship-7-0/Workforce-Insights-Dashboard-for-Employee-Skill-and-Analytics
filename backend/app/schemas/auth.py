"""Auth request/response schemas."""

from pydantic import BaseModel, EmailStr, Field

from app.schemas.admin import AdminOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminOut


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
