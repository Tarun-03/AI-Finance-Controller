from fastapi import FastAPI

from app.api.router import api_router


app = FastAPI(
    title="AI Finance Controller",
    description=(
        "Agentic AI-powered finance reconciliation platform"
    ),
    version="0.1.0",
)


app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "AI Finance Controller API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }