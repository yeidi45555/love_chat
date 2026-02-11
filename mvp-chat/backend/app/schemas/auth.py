from pydantic import BaseModel, EmailStr
from datetime import date

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    birthdate: date | None = None
    gender: str | None = None

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"

class RefreshIn(BaseModel):
    refresh_token: str
