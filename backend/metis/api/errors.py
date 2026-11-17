from fastapi import Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException


def _es_error_de_la_app(detail: object) -> bool:
    return (
        isinstance(detail, dict)
        and isinstance(detail.get("error"), dict)
        and isinstance(detail["error"].get("codigo"), str)
    )


async def manejar_http_exception(
    request: Request, exc: StarletteHTTPException
) -> Response:
    """Estructura de error estándar (`api-contracts.md`): `{"error": {codigo,
    mensaje}}` en el body, sin envolver.

    Los endpoints levantan `HTTPException(detail={"error": {...}})`, y el
    manejador por defecto de FastAPI lo serializa como `{"detail": {"error":
    {...}}}`: `frontend/src/api/client.ts::toApiError()` no reconocía el código
    y mostraba el texto genérico (ej. login con contraseña incorrecta). Acá se
    desenvuelve. Cualquier otro `detail` (un str como "No autenticado", el 404
    de ruta inexistente) sigue por el manejador por defecto, sin cambios.
    """
    if _es_error_de_la_app(exc.detail):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
            headers=getattr(exc, "headers", None),
        )
    return await http_exception_handler(request, exc)
