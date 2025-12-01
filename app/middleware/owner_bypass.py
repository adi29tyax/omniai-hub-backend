from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from jose import jwt, JWTError
from app.config import settings

OWNER_EMAIL = "csadityasharma2000@gmail.com"

class OwnerBypassMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.owner_mode = False

        if not settings.OWNER_MODE:
             return await call_next(request)

        # 1. Check if user is already attached (rare in middleware)
        user = getattr(request.state, "user", None)
        if user and hasattr(user, "email") and user.email == OWNER_EMAIL:
            request.state.owner_mode = True
        
        # 2. If not, try to decode token from header
        if not request.state.owner_mode:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALG])
                    email = payload.get("sub")
                    if email == OWNER_EMAIL:
                        request.state.owner_mode = True
                except JWTError:
                    pass # Invalid token, ignore

        response = await call_next(request)
        return response
