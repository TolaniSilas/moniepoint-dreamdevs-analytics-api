"""Aggregates all API v1 route modules."""
from fastapi import APIRouter
from src.api.v1.endpoints import analytics


# create main API router.
api_router = APIRouter()

# include sub-routers from endpoint modules.
api_router.include_router(analytics.router)
