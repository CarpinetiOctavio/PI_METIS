import uuid

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombre: str | None = None

    @field_validator("email")
    @classmethod
    def email_must_be_ucc(cls, v: str) -> str:
        if not v.endswith("@ucc.edu.ar"):
            raise ValueError("El email debe ser @ucc.edu.ar")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyRequest(BaseModel):
    token: str


class UserMe(BaseModel):
    id: uuid.UUID
    email: EmailStr
    nombre: str | None
    email_verified: bool
