from pydantic import BaseModel


class ErrorDetail(BaseModel):
    codigo: str
    mensaje: str
    detalle: dict = {}


class ErrorResponse(BaseModel):
    error: ErrorDetail
