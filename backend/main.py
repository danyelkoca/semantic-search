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

# Set allowed origins based on the FRONT_END_URL environment variable
origins = [os.getenv("FRONT_END_URL")]

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
