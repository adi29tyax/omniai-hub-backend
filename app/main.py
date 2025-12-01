from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.database import engine, Base

from app.modules.director.router import router as director_router
from app.modules.assistant.assistant_router import router as assistant_router
from app.modules.projects.router import router as projects_router
from app.modules.project_files.router import router as project_files_router
from app.modules.director.timeline_router import router as timeline_router
from app.modules.director.audio_router import router as audio_router
from app.modules.director.breakdown_router import router as breakdown_router
from app.modules.director.keyframe_router import router as keyframe_router
from app.modules.director.animation_router import router as animation_router
from app.routers.director_auto import router as director_auto_router
from app.routers.render_router import router as render_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniAI Studio Universe API — Stable v2.0",
    description="Owner Edition: Unlimited Access",
    version="2.0.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url=None,
    swagger_ui_parameters={"persistAuthorization": True},
    debug=False
)

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="OmniAI Studio Universe API — Stable v2.0",
        version="2.0.0",
        description="Owner Edition: Unlimited Access",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Ensure /auth/me endpoint has security requirement
    if "paths" in openapi_schema and "/auth/me" in openapi_schema["paths"]:
        if "get" in openapi_schema["paths"]["/auth/me"]:
            openapi_schema["paths"]["/auth/me"]["get"]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Add HSTS if using HTTPS in production
        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# CORS
# Restrict to ["*"] as per Phase 15.1 instructions for now, but ideally should be specific.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Global Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log error here if logger available
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc) if settings.APP_ENV != "production" else "An unexpected error occurred."},
    )

from app.modules.billing.billing_router import router as billing_router
from app.routers.auth import router as auth_router
from app.routers.system import router as system_router
from app.middleware.usage_limit import check_usage_limit
from app.middleware.owner_bypass import OwnerBypassMiddleware
from app.middleware.error_handler import GlobalExceptionMiddleware
from fastapi import Depends

app.add_middleware(GlobalExceptionMiddleware)
app.add_middleware(OwnerBypassMiddleware)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(system_router, prefix="/system", tags=["System"])
app.include_router(billing_router, prefix="/billing", tags=["Billing"])

# Apply usage limits to protected routes
app.include_router(director_router, prefix="/director", tags=["Director"], dependencies=[Depends(check_usage_limit)])
app.include_router(assistant_router, prefix="/assistant", tags=["AI Assistant"], dependencies=[Depends(check_usage_limit)])
app.include_router(projects_router, prefix="/projects", tags=["Projects"])
app.include_router(project_files_router, prefix="/project-files", tags=["Project Files"])
app.include_router(timeline_router, prefix="/director", tags=["Timeline"], dependencies=[Depends(check_usage_limit)])
app.include_router(audio_router, prefix="/audio", tags=["Audio"], dependencies=[Depends(check_usage_limit)])
app.include_router(breakdown_router, prefix="/director", tags=["Breakdown"], dependencies=[Depends(check_usage_limit)])
app.include_router(keyframe_router, prefix="/director", tags=["Keyframe"], dependencies=[Depends(check_usage_limit)])
app.include_router(animation_router, prefix="/director", tags=["Animation"], dependencies=[Depends(check_usage_limit)])
from app.routers.director_scene import router as director_scene_router
from app.routers.director_shot import router as director_shot_router
from app.routers.director_keyframe import router as director_keyframe_router
from app.routers.director_animation import router as director_animation_router
from app.routers.director_timeline import router as director_timeline_router

app.include_router(director_scene_router, prefix="/director/scene", tags=["Director - Scene Breakdown"], dependencies=[Depends(check_usage_limit)])
app.include_router(director_shot_router, prefix="/director/shot", tags=["Director - Shot Breakdown"], dependencies=[Depends(check_usage_limit)])
app.include_router(director_keyframe_router, prefix="/director/keyframe", tags=["Director - Keyframe Generator"], dependencies=[Depends(check_usage_limit)])
app.include_router(director_animation_router, prefix="/director/animation", tags=["Animation"], dependencies=[Depends(check_usage_limit)])
app.include_router(director_timeline_router, prefix="/director/timeline", tags=["Timeline"], dependencies=[Depends(check_usage_limit)])
app.include_router(director_auto_router, prefix="/director/auto", tags=["AutoDirector"], dependencies=[Depends(check_usage_limit)])
app.include_router(render_router, prefix="/render", tags=["Render"], dependencies=[Depends(check_usage_limit)])

@app.get("/health")
async def health():
    return {"status": "ok", "service": "OmniAI API", "env": settings.APP_ENV}
