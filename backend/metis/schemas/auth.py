import uuid

from pydantic import BaseModel, EmailStr


class UserMe(BaseModel):
    id: uuid.UUID
    email: EmailStr
    nombre: str | None
