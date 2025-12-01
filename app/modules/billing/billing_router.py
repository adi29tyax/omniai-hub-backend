from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from .billing_schemas import PaymentRequest, PaymentStatus
from .billing_service import BillingService

router = APIRouter()

@router.post("/create-checkout-session", response_model=PaymentStatus)
async def create_checkout_session(
    request: PaymentRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = BillingService(db)
    if request.payment_method == "stripe":
        return await service.create_stripe_session(user, request.plan_id)
    elif request.payment_method == "razorpay":
        return await service.create_razorpay_order(user, request.plan_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    service = BillingService(db)
    return await service.handle_stripe_webhook(request)

@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    service = BillingService(db)
    return await service.handle_razorpay_webhook(request)

@router.get("/status")
async def get_billing_status(request: Request, user: User = Depends(get_current_user)):
    if getattr(request.state, "owner_mode", False):
        return {
            "status": "approved",
            "plan": "unlimited",
            "credits": "infinite",
            "limit": "none"
        }
    return {"role": user.role, "plan": user.role}
