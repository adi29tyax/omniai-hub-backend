import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log slow requests (> 2 seconds)
        if process_time > 2.0:
            logger.warning(f"SLOW REQUEST: {request.method} {request.url.path} took {process_time:.2f}s")
        
        # Add header for debugging
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
