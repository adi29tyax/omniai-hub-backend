from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/status")
async def system_status(request: Request):
    owner_mode = getattr(request.state, "owner_mode", False)
    return {
        "system": "OmniAI Studio Universe",
        "status": "running",
        "environment": "development",
        "owner_mode": owner_mode,
        "plan": "unlimited" if owner_mode else "free",
        "limits": "none" if owner_mode else "standard",
        "version": "1.0.0-owner",
        "release": "Stable",
        "build": "OmniAI Studio Universe — Owner Edition",
        "owner_banner": "OWNER MODE ACTIVE — Unlimited Access" if owner_mode else None
    }
