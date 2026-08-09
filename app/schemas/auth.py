from pydantic import BaseModel, EmailStr, Field


class TrainerRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=100)


class TrainerLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TrainerResponse(BaseModel):
    id: str
    email: EmailStr
    display_name: str
    is_active: bool