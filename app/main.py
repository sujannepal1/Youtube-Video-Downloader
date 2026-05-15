from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import async_engine
from app.routes import router
from models.song import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup using the async engine."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="YT Audio Dataset API",
    description="Download YouTube audio and store metadata for music classification.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "YT Audio Dataset API is running."}
