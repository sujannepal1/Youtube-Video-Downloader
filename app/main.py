import logging
import logging.config
import time

from fastapi import FastAPI, Request

from app.routes import router

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "app": {"level": "DEBUG", "propagate": True},
        "uvicorn.access": {"level": "INFO", "propagate": True},
        "uvicorn.error": {"level": "INFO", "propagate": True},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YT Audio Dataset API",
    description="Download YouTube audio and store metadata for music classification.",
    version="1.0.0",
)

app.include_router(router, prefix="/api")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    logger.info("→ %s %s  client=%s", request.method, request.url.path, request.client.host if request.client else "unknown")
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    logger.info("← %s %s  status=%d  %.1fms", request.method, request.url.path, response.status_code, elapsed)
    return response


@app.get("/")
async def root():
    logger.debug("Health-check endpoint called")
    return {"message": "YT Audio Dataset API is running."}
