import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.middleware import (
    custom_http_exception_handler,
    generic_exception_handler,
    lifespan,
    log_error_responses,
    log_slow_requests,
    validation_exception_handler,
)
from app.routes import routers

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Semantic Fashion Recommendation System",
    description="A semantic search API for fashion recommendations.",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.middleware("http")(log_slow_requests)
app.middleware("http")(log_error_responses)

# Global rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Read environment
env = os.getenv("ENV", "development").lower()

# Choose correct frontend URL based on environment
if env == "production":
    raw_origins = os.getenv("PROD_FRONTEND_URL", "")
else:
    raw_origins = os.getenv("DEV_FRONTEND_URL", "")

# Parse and clean allowed origins
allowed_origins = [
    origin.strip() for origin in raw_origins.split(",") if origin.strip()
]

# Fail early if no allowed origins
if not allowed_origins:
    raise ValueError("No allowed origins specified for environment: " + env)

# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Authorization", "Content-Type"],
)

# Centralized Exception Handlers
app.exception_handler(Exception)(generic_exception_handler)
app.exception_handler(RequestValidationError)(validation_exception_handler)
app.exception_handler(HTTPException)(custom_http_exception_handler)

# Include all API routers (each router should use app.state.limiter)
for router in routers:
    app.include_router(router)
