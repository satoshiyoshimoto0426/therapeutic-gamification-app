#!/usr/bin/env python3
"""
Simple test service to verify basic FastAPI functionality
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Test Service",
    description="Simple test service for deployment verification",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Test service is running!", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "test"}

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "API endpoint working",
        "timestamp": "2025-07-29",
        "data": {"test": True}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)