from fastapi import APIRouter

from app.api.routes import (
    agent,
    exceptions,
    reconciliation,
    transactions,
)


api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(
    transactions.router,
)

api_router.include_router(
    reconciliation.router,
)

api_router.include_router(
    exceptions.router,
)

api_router.include_router(
    agent.router,
)