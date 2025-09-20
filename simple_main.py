"""
Simple API server for testing intelligence features.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.intelligence import intelligence

# Create FastAPI application
app = FastAPI(
    title="PolicyEdgeAI Intelligence",
    description="Intelligence feed and memo generation for PolicyEdgeAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include intelligence router
app.include_router(intelligence)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "intelligence"}

if __name__ == "__main__":
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)