# Root compatibility wrapper delegating to app.api.v1.schemes
from app.api.v1.schemes import router

__all__ = ["router"]