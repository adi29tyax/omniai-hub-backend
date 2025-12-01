from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback

class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            error_message = str(e)
            traceback_str = traceback.format_exc()

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": error_message,
                    "trace": traceback_str
                }
            )
