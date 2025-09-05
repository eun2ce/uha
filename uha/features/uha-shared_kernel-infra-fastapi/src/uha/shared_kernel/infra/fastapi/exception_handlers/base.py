from fastapi import Request
from fastapi.responses import JSONResponse

from uha.shared_kernel.domain.exception import BaseMsgException


async def custom_exception_handler(request: Request, exc: BaseMsgException) -> JSONResponse:
    """Custom exception handler for application exceptions."""
    return JSONResponse(
        status_code=exc.code,
        content={
            "status": "error",
            "message": exc.message,
            "error": exc.error,
        },
    )
