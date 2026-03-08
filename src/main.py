"""fastapi application entrypoint - Moniepoint Analytics API."""
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from src.api.v1.router import api_router
from sqlalchemy import text              
from sqlalchemy.exc import OperationalError  
from src.db.base import engine       


# configure logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),      
        logging.FileHandler("app.log"), 
    ]
)

# logger for request logging middleware.
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


# initialize the fastapi application with metadata and lifespan handler.
app = FastAPI(
    title="Moniepoint Analytics API",
    description="REST API endpoints for merchant activity analytics",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """log every incoming request with method, path, status code, and response time."""

    # record the time before the request is processed.
    start_time = time.perf_counter()

    # pass the request to the next handler (endpoint) and get the response.
    response = await call_next(request)

    # calculate total request duration in milliseconds.
    duration_ms = (time.perf_counter() - start_time) * 1000

    # log request details for developer visibility into API usage and performance.
    logger.info(
        "%s %s %s %.2fms",
        request.method, 
        request.url.path,    
        response.status_code, 
        duration_ms,         
    )

    return response


# include all API routes under /api/v1.
app.include_router(api_router)


# health check endpoint - verifies the API is running and the database is reachable.
@app.get("/")
def root():
    """health check endpoint: verifies API is running and database is reachable."""

    try:
        # attempt a lightweight DB ping to confirm the database is reachable.
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"

    except OperationalError:
        # log the db failure server-side for developer debugging.
        logger.error("health check failed: database is unreachable.")
        db_status = "unreachable"

    return {
        "service": "Moniepoint Analytics API",
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
    }