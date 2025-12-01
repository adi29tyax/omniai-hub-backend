from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.user_usage import UserUsage
from app.modules.billing.subscription_plans import PLANS
from app.deps import get_current_user
import logging

logger = logging.getLogger(__name__)

async def check_usage_limit(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Owner Bypass
    if getattr(request.state, "owner_mode", False):
        return

    # 2. Load Usage
    usage = db.query(UserUsage).filter(UserUsage.user_id == user.id).first()
    if not usage:
        usage = UserUsage(user_id=user.id)
        db.add(usage)
        db.commit()
        db.refresh(usage)

    # 3. Get Plan Limits
    plan = PLANS.get(user.role, PLANS["free"])

    # 4. Check Limits based on endpoint
    path = request.url.path
    
    if "/director" in path or "/auto-director" in path:
        # Check episode limit
        if usage.episodes_generated >= plan.episodes_per_day:
             raise HTTPException(status_code=403, detail={"error": "LimitReached", "message": "Daily episode limit reached. Upgrade to continue."})
        usage.episodes_generated += 1

    elif "/assistant" in path:
        # Check AI calls
        if usage.ai_calls >= plan.ai_calls_per_day:
            raise HTTPException(status_code=403, detail={"error": "LimitReached", "message": "Daily AI call limit reached. Upgrade to continue."})
        usage.ai_calls += 1
        
    # Commit usage increment
    db.commit()
