from fastapi import FastAPI

from app.routes import router

app = FastAPI(
    title="YT Audio Dataset API",
    description="Download YouTube audio and store metadata for music classification.",
    version="1.0.0",
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "YT Audio Dataset API is running."}
