import logging
from typing import Any, Dict
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.core.exceptions")


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class SchemeNotFoundException(AppException):
    """Raised when a requested scheme is not found."""

    def __init__(self, scheme_id: int):
        super().__init__(
            message=f"Scheme with ID {scheme_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        self.scheme_id = scheme_id


class ProgramNotFoundException(AppException):
    """Raised when a requested government programme is not found."""

    def __init__(self, identifier: Any):
        super().__init__(
            message=f"Government programme '{identifier}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        self.identifier = identifier


class InvalidFilterException(AppException):
    """Raised when invalid filtering parameters are supplied."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.message = message


class DatabaseConnectionException(AppException):
    """Raised when database connection fails."""

    def __init__(self, message: str = "Database connection error"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with FastAPI."""

    @app.exception_handler(SchemeNotFoundException)
    async def scheme_not_found_handler(request: Request, exc: SchemeNotFoundException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Not Found",
                "detail": exc.message,
                "scheme_id": exc.scheme_id,
            },
        )

    @app.exception_handler(ProgramNotFoundException)
    async def program_not_found_handler(request: Request, exc: ProgramNotFoundException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Not Found",
                "detail": exc.message,
                "identifier": str(exc.identifier),
            },
        )

    @app.exception_handler(InvalidFilterException)
    async def invalid_filter_handler(request: Request, exc: InvalidFilterException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Bad Request",
                "detail": exc.message,
            },
        )

    @app.exception_handler(DatabaseConnectionException)
    async def db_connection_handler(request: Request, exc: DatabaseConnectionException) -> JSONResponse:
        logger.error(f"Database error: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Service Unavailable",
                "detail": "Database is temporarily unreachable. Please try again later.",
            },
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        error_name = (
            "Bad Request"
            if exc.status_code == status.HTTP_400_BAD_REQUEST
            else "Not Found"
            if exc.status_code == status.HTTP_404_NOT_FOUND
            else "Error"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": error_name,
                "detail": exc.message,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error occurred")
        # Do not expose internal traceback or DB info
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred. Please contact support.",
            },
        )
