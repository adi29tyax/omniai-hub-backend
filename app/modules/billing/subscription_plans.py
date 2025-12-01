from .billing_schemas import SubscriptionPlan

PLANS = {
    "free": SubscriptionPlan(
        name="Free",
        episodes_per_day=1,
        ai_calls_per_day=20,
        storage_limit_mb=150,
        price_usd=0
    ),
    "pro": SubscriptionPlan(
        name="Pro",
        episodes_per_day=20,
        ai_calls_per_day=999999, # Unlimited
        storage_limit_mb=2048,
        price_usd=29
    ),
    "ultra": SubscriptionPlan(
        name="Ultra",
        episodes_per_day=999999, # Unlimited
        ai_calls_per_day=999999, # Unlimited
        storage_limit_mb=999999, # Unlimited
        price_usd=99
    )
}
