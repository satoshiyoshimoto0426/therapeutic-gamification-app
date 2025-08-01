
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Auth Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Auth service is running!", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth"}

@app.get("/api/status")
async def status():
    return {
        "service": "Auth",
        "port": 8002,
        "timestamp": "2025-07-29T17:14:35.521815",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
