"""fastapi application entrypoint - Moniepoint Analytics API."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Moniepoint Analytics API",
    description="REST API endpoints for merchant activity analytics",
    lifespan=lifespan,
)

# include all API routes under /api/v1
app.include_router(api_router)


# simple root endpoint for health check and sanity check.
@app.get("/")
def root():
    """a get api endpoint for health check and sanity check."""
    
    return {"service": "Moniepoint Analytics API", "status": "ok"}
