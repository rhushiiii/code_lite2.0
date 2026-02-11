from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)


class UserLogin(UserBase):
    password: str = Field(min_length=8, max_length=72)


class UserOut(UserBase):
    id: int
    github_connected: bool = False
    github_username: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
