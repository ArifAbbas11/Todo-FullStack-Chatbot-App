"""
FastAPI application entry point.
Configures CORS, middleware, and registers API routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.database import create_db_and_tables
from src.api import auth, tasks, chat

# Create FastAPI application instance
app = FastAPI(
    title="Todo API",
    description="RESTful API for Todo Full-Stack Web Application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",  # Local development
        "https://todo-full-stack-app-tau.vercel.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.on_event("startup")
async def on_startup():
    """
    Application startup event handler.
    Creates database tables if they don't exist.
    """
    create_db_and_tables()


@app.get("/health")
async def health_check():
    """
    Health check endpoint for deployment monitoring.

    Returns:
        dict: Status message
    """
    return {"status": "healthy", "message": "Todo API is running"}


@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: API information
    """
    return {
        "message": "Todo API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Register API routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(tasks.router, tags=["Tasks"])
app.include_router(chat.router, tags=["Chat"])
