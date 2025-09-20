"""
PolicyEdgeAI - Main FastAPI application
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize API keys from environment
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Log API configuration 
logger.info(f"OpenAI API configured: {bool(openai_api_key)}")
logger.info(f"Anthropic API configured: {bool(anthropic_api_key)}")

# Initialize application
app = FastAPI(
    title="PolicyEdgeAI",
    description="Enterprise compliance automation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for web interface
try:
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    templates = Jinja2Templates(directory="frontend/templates")
except:
    logger.warning("Frontend directories not found. Web interface will not be available.")

# Include routers that are known to exist
from api.endpoints import create_api
from api.health import router as health_router

# Include health router
app.include_router(health_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "PolicyEdgeAI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Run application
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    
    # Run application
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)