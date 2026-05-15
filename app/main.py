from fastapi import FastAPI

from app.database import engine
from app.routes import router
from models.song import Base

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="YT Audio Dataset API",
    description="Download YouTube audio and store metadata for music classification.",
    version="1.0.0",
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "YT Audio Dataset API is running."}
