"""pydantic schemas for analytics API responses (for responses validaton)."""
from pydantic import BaseModel, ConfigDict


class TopMerchantResponse(BaseModel):
    """merchant with highest total successful transaction volume."""

    merchant_id: str | None
    total_volume: float

    model_config = ConfigDict(json_schema_extra={"an instance": {"merchant_id": "MRC-001234", "total_volume": 98765432.10}})


class MonthlyActiveMerchantsResponse(BaseModel):
    """unique merchants per month (at least one successful event)."""

    model_config = ConfigDict(extra="allow") 


class ProductAdoptionResponse(BaseModel):
    """unique merchant count per product."""

    model_config = ConfigDict(extra="allow") 


class KycFunnelResponse(BaseModel):
    """KYC conversion funnel counts."""

    documents_submitted: int
    verifications_completed: int
    tier_upgrades: int


class FailureRateItem(BaseModel):
    """failure rate for one product."""

    product: str
    failure_rate: float
