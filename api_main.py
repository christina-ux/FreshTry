from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="PolicyEdgeAI API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"message": "Welcome to PolicyEdgeAI API"}

@app.get("/api-keys")
def api_keys_info():
    openai_key = os.getenv("OPENAI_API_KEY", "Not configured")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "Not configured")
    
    # Only show if keys are configured, not the actual keys
    return {
        "openai": "Configured" if openai_key \!= "Not configured" else "Not configured",
        "anthropic": "Configured" if anthropic_key \!= "Not configured" else "Not configured"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
