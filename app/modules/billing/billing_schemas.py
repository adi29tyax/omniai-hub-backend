from pydantic import BaseModel
from typing import Optional

class SubscriptionPlan(BaseModel):
    name: str
    episodes_per_day: int
    ai_calls_per_day: int
    storage_limit_mb: int
    price_usd: float

class PaymentRequest(BaseModel):
    plan_id: str # 'pro' or 'ultra'
    payment_method: str # 'stripe' or 'razorpay'

class PaymentStatus(BaseModel):
    status: str
    checkout_url: Optional[str] = None
    order_id: Optional[str] = None
