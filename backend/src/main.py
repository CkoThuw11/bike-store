from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exception_handlers import register_exception_handlers
from src.api.routes import (
    auth_router,
    brands,
    categories,
    customers,
    orderitems,
    orders,
    products,
    staffs,
    stocks,
    stores,
)
from src.core.logging_config import setup_logging
from src.core.middleware import RequestLoggingMiddleware
from src.infrastructure.configs import settings
from src.infrastructure.connection import engine, get_db

setup_logging(settings.app.log_level, settings.app.log_format)
logger = structlog.get_logger(__name__)


# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting application...")
    yield

    logger.info("Shutting down application...")
    await engine.dispose()
    logger.info("Database connections closed.")


# --- App ---
app = FastAPI(
    title="Bike Store API",
    description="A structured, production-ready backend system demonstrating Clean Architecture.",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Exception Handlers ---
register_exception_handlers(app)


# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)


# --- Routers ---
app.include_router(auth_router.router)
app.include_router(brands.router)
app.include_router(categories.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(orderitems.router)
app.include_router(products.router)
app.include_router(staffs.router)
app.include_router(stocks.router)
app.include_router(stores.router)


# --- Health & Readiness ---
@app.get("/health", include_in_schema=True, tags=["Health"])
async def health_check() -> dict:
    """Liveness probe — always returns ok if the process is up."""
    return {"status": "ok"}


@app.get("/ready", include_in_schema=True, tags=["Health"])
async def readiness_check(session: AsyncSession = Depends(get_db)) -> dict:
    """Readiness probe — verifies database connectivity."""
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
