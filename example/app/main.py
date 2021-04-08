"""Main entry point for application"""

import os
import logging
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status, Request
from .api import auth_api, client_api, provider_api, blockchain_api
import uuid

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

logging.info("Starting")

if 'ENVIRONMENT' not in os.environ or os.environ['ENVIRONMENT'] == 'development':
    logging.info("Development CORS policy enabled")
    middleware = [ Middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:3000', 'http://localhost:*', 'https://app.dev.blockmedisolutions.com'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )]


app = FastAPI(middleware=middleware)

@app.middleware("http")
async def add_correlation_header(request: Request, call_next):    
    correlation_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Correlation-Id"] = correlation_id
    return response

app.include_router(auth_api)
app.include_router(client_api)
app.include_router(provider_api)
app.include_router(blockchain_api)

@app.get('/api/health', status_code=status.HTTP_200_OK)
def health():
    """Health check endpoint for use by ECS"""
    return True

