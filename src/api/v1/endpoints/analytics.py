"""analytics endpoints: GET /analytics/*."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.deps import get_db
from src.schemas.analytics import FailureRateItem, KycFunnelResponse, MonthlyActiveMerchantsResponse, ProductAdoptionResponse, TopMerchantResponse
from src.services.analytics import AnalyticsService


# the logger inherits basicConfig set up in main.py.
logger = logging.getLogger(__name__)


# create router for analytics endpoints.
router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:

    return AnalyticsService(db)


@router.get("/top-merchant", response_model=TopMerchantResponse)
def top_merchant(service: AnalyticsService = Depends(get_analytics_service)):
    """merchant with highest total successful transaction amount across all products."""

    try:
        return service.get_top_merchant()

    except RuntimeError as e:
        # log full error details server-side for developer debugging — never exposed to client.
        logger.error("Service error in top_merchant endpoint: %s", e)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again later.")

    except Exception as e:
        # log full traceback server-side for unknown errors — never exposed to client.
        logger.error("Unexpected error in top_merchant endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.get("/monthly-active-merchants", response_model=MonthlyActiveMerchantsResponse)
def monthly_active_merchants(service: AnalyticsService = Depends(get_analytics_service)):
    """unique merchants with at least one successful event per month."""

    try:
        return service.get_monthly_active_merchants()

    except RuntimeError as e:
        # log full error details server-side for developer debugging — never exposed to client.
        logger.error("Service error in monthly_active_merchants endpoint: %s", e)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again later.")

    except Exception as e:
        # log full traceback server-side for unknown errors — never exposed to client.
        logger.error("Unexpected error in monthly_active_merchants endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.get("/product-adoption", response_model=ProductAdoptionResponse)
def product_adoption(service: AnalyticsService = Depends(get_analytics_service)):
    """unique merchant count per product (sorted by count, highest first)."""

    try:
        return service.get_product_adoption()

    except RuntimeError as e:
        # log full error details server-side for developer debugging — never exposed to client.
        logger.error("Service error in product_adoption endpoint: %s", e)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again later.")

    except Exception as e:
        # log full traceback server-side for unknown errors — never exposed to client.
        logger.error("Unexpected error in product_adoption endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.get("/kyc-funnel", response_model=KycFunnelResponse)
def kyc_funnel(service: AnalyticsService = Depends(get_analytics_service)):
    """kyc conversion funnel (unique merchants at each stage, successful events only)."""

    try:
        return service.get_kyc_funnel()

    except RuntimeError as e:
        # log full error details server-side for developer debugging — never exposed to client.
        logger.error("Service error in kyc_funnel endpoint: %s", e)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again later.")

    except Exception as e:
        # log full traceback server-side for unknown errors — never exposed to client.
        logger.error("Unexpected error in kyc_funnel endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.get("/failure-rates", response_model=list[FailureRateItem])
def failure_rates(service: AnalyticsService = Depends(get_analytics_service)):
    """failure rate per product; exclude PENDING; sort by rate descending."""

    try:
        return service.get_failure_rates()

    except RuntimeError as e:
        # log full error details server-side for developer debugging — never exposed to client.
        logger.error("Service error in failure_rates endpoint: %s", e)
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again later.")

    except Exception as e:
        # log full traceback server-side for unknown errors — never exposed to client.
        logger.error("Unexpected error in failure_rates endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")