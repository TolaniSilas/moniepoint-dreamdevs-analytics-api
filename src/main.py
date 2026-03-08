"""fastapi application entrypoint - Moniepoint Analytics API."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.v1.router import api_router


# configure logging once at app startup so all modules inherit this setup.
# logs are written to both the terminal and app.log file on disk for dev debugging.
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),         
        logging.FileHandler("app.log"),
    ]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Moniepoint Analytics API",
    description="REST API endpoints for merchant activity analytics",
    lifespan=lifespan,
)

# include all API routes under /api/v1.
app.include_router(api_router)


# simple root endpoint for health check and sanity check.
@app.get("/")
def root():
    """a get api endpoint for health check and sanity check."""
    
    return {"service": "Moniepoint Analytics API", "status": "ok"}
