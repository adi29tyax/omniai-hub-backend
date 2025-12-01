from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user_usage import UserUsage
from .billing_schemas import PaymentStatus
from fastapi import Request
import datetime

# Mock services for now
class BillingService:
    def __init__(self, db: Session):
        self.db = db

    async def create_stripe_session(self, user: User, plan_id: str) -> PaymentStatus:
        # Mock Stripe implementation
        return PaymentStatus(
            status="success",
            checkout_url=f"https://checkout.stripe.com/pay/{plan_id}?user={user.id}"
        )

    async def create_razorpay_order(self, user: User, plan_id: str) -> PaymentStatus:
        # Mock Razorpay implementation
        return PaymentStatus(
            status="created",
            order_id=f"order_{plan_id}_{user.id}"
        )

    async def handle_stripe_webhook(self, request: Request):
        # Mock webhook handler
        # In real implementation, verify signature and update user role
        return {"status": "received"}

    async def handle_razorpay_webhook(self, request: Request):
        # Mock webhook handler
        return {"status": "received"}

    def upgrade_user(self, user_id: int, plan_id: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.role = plan_id
            # Reset usage
            usage = self.db.query(UserUsage).filter(UserUsage.user_id == user_id).first()
            if not usage:
                usage = UserUsage(user_id=user_id)
                self.db.add(usage)
            
            usage.episodes_generated = 0
            usage.ai_calls = 0
            usage.storage_used_mb = 0
            usage.last_reset = datetime.datetime.utcnow()
            
            self.db.commit()
