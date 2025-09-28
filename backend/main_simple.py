#!/usr/bin/env python3
"""
NEXUS Platform - Simplified Backend
Minimal working backend for testing
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting NEXUS Platform Backend...")
    yield
    # Shutdown
    logger.info("Shutting down NEXUS Platform Backend...")

# Create FastAPI app
app = FastAPI(
    title="NEXUS Platform API",
    description="Simplified NEXUS Platform Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "NEXUS Platform API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "nexus-backend",
        "version": "1.0.0"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "endpoints": ["/", "/health", "/api/status"],
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
