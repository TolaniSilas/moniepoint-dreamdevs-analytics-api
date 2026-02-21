"""Analytics endpoints: GET /analytics/*."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.deps import get_db
from src.schemas.analytics import (
    FailureRateItem,
    KycFunnelResponse,
    MonthlyActiveMerchantsResponse,
    ProductAdoptionResponse,
    TopMerchantResponse,
)
from src.services.analytics import AnalyticsService

# create router for analytics endpoints.
router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:

    return AnalyticsService(db)


@router.get("/top-merchant", response_model=TopMerchantResponse)
def top_merchant(service: AnalyticsService = Depends(get_analytics_service)):
    """merchant with highest total successful transaction amount across all products."""

    return service.get_top_merchant()


@router.get("/monthly-active-merchants", response_model=MonthlyActiveMerchantsResponse)
def monthly_active_merchants(service: AnalyticsService = Depends(get_analytics_service)):
    """unique merchants with at least one successful event per month."""

    return service.get_monthly_active_merchants()


@router.get("/product-adoption", response_model=ProductAdoptionResponse)
def product_adoption(service: AnalyticsService = Depends(get_analytics_service)):
    """unique merchant count per product (sorted by count, highest first)."""

    return service.get_product_adoption()


@router.get("/kyc-funnel", response_model=KycFunnelResponse)
def kyc_funnel(service: AnalyticsService = Depends(get_analytics_service)):
    """KYC conversion funnel (unique merchants at each stage, successful events only)."""

    return service.get_kyc_funnel()


@router.get("/failure-rates", response_model=list[FailureRateItem])
def failure_rates(service: AnalyticsService = Depends(get_analytics_service)):
    """failure rate per product; exclude PENDING; sort by rate descending."""

    return service.get_failure_rates()

