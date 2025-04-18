import logging
import os

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

# Setup environment-based log level
env = os.getenv("ENV", "development")
log_level = logging.INFO if env == "production" else logging.DEBUG

logger = logging.getLogger("semantic-search")
logger.setLevel(log_level)

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
)
logger.addHandler(console_handler)

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

# CORS Middleware
origins = (
    [
        "http://localhost:4173",
        "http://localhost:5173",
    ]
    if env != "production"
    else [os.getenv("FRONTEND_URL")]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
