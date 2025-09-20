from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime, timedelta
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

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Model Definitions
class User(BaseModel):
    id: int
    name: str
    email: str
    company: Optional[str] = None

class Policy(BaseModel):
    id: int
    name: str
    type: str
    user_id: int
    upload_date: str
    status: str
    content_preview: Optional[str] = None

class AnalysisResult(BaseModel):
    id: int
    policy_id: int
    analysis_type: str
    summary: str
    compliance: Dict[str, str]
    readability: str
    insights: List[str]
    created_at: str

# Mock Data
users = [
    {
        "id": 1,
        "name": "Demo User",
        "email": "demo@example.com",
        "password": "password123",
        "company": "PolicyEdgeAI"
    }
]

policies = []

analysis_results = []

# Helper functions
def get_user(email: str):
    for user in users:
        if user["email"] == email:
            return user
    return None

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if user["password"] \!= password:  # In a real app, use proper password hashing
        return False
    return user

def create_token(data: dict):
    # Simplified token - in a real app, use JWT
    return f"token_{data['sub']}_{datetime.now().timestamp()}"

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Simplified auth - in a real app, validate JWT properly
    try:
        user_id = int(token.split("_")[1])
        for user in users:
            if user["id"] == user_id:
                return user
    except:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to PolicyEdgeAI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api-keys")
def api_keys_info():
    openai_key = os.getenv("OPENAI_API_KEY", "Not configured")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "Not configured")
    
    # Only show if keys are configured, not the actual keys
    return {
        "openai": "Configured" if openai_key \!= "Not configured" else "Not configured",
        "anthropic": "Configured" if anthropic_key \!= "Not configured" else "Not configured"
    }

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_token({"sub": str(user["id"])})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/users")
def register_user(name: str = Form(...), email: str = Form(...), password: str = Form(...), company: Optional[str] = Form(None)):
    if get_user(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = {
        "id": len(users) + 1,
        "name": name,
        "email": email,
        "password": password,  # In a real app, hash this password
        "company": company
    }
    
    users.append(new_user)
    
    return {"message": "User registered successfully"}

@app.get("/users/me", response_model=User)
def get_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "company": current_user["company"]
    }

@app.post("/policies")
async def upload_policy(
    policy_name: str = Form(...),
    policy_type: str = Form(...),
    file: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    # In a real app, store the file and process it
    content = await file.read()
    content_preview = content[:500].decode("utf-8", errors="ignore") if content else ""
    
    new_policy = {
        "id": len(policies) + 1,
        "name": policy_name,
        "type": policy_type,
        "user_id": current_user["id"],
        "upload_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "Uploaded",
        "content_preview": content_preview,
        "notes": notes
    }
    
    policies.append(new_policy)
    
    return {
        "message": "Policy uploaded successfully",
        "policy_id": new_policy["id"]
    }

@app.get("/policies", response_model=List[Policy])
def get_policies(current_user: dict = Depends(get_current_user)):
    user_policies = [
        {
            "id": p["id"],
            "name": p["name"],
            "type": p["type"],
            "user_id": p["user_id"],
            "upload_date": p["upload_date"],
            "status": p["status"],
            "content_preview": p["content_preview"][:100] if p.get("content_preview") else None
        }
        for p in policies if p["user_id"] == current_user["id"]
    ]
    
    return user_policies

@app.get("/policies/{policy_id}", response_model=Policy)
def get_policy(policy_id: int, current_user: dict = Depends(get_current_user)):
    for policy in policies:
        if policy["id"] == policy_id and policy["user_id"] == current_user["id"]:
            return {
                "id": policy["id"],
                "name": policy["name"],
                "type": policy["type"],
                "user_id": policy["user_id"],
                "upload_date": policy["upload_date"],
                "status": policy["status"],
                "content_preview": policy["content_preview"]
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Policy not found"
    )

@app.post("/analysis")
def analyze_policy(
    policy_id: int,
    analysis_type: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    # Check if policy exists and belongs to user
    policy = None
    for p in policies:
        if p["id"] == policy_id and p["user_id"] == current_user["id"]:
            policy = p
            break
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Mock analysis results based on policy type
    if policy["type"] == "Privacy Policy":
        compliance = {
            "GDPR": "87% compliant",
            "CCPA": "92% compliant",
            "HIPAA": "Not applicable"
        }
        insights = [
            "Consider simplifying language in data collection sections",
            "Missing clear data retention guidelines",
            "Strong on consent mechanisms"
        ]
    elif policy["type"] == "Terms of Service":
        compliance = {
            "Consumer Protection": "76% compliant",
            "E-Commerce Regulations": "88% compliant"
        }
        insights = [
            "Liability clauses may be overly broad",
            "Consider adding clearer dispute resolution terms",
            "Good coverage of intellectual property rights"
        ]
    else:
        compliance = {
            "General": "82% compliant"
        }
        insights = [
            "Some sections use overly complex language",
            "Consider adding more examples or clarifications",
            "Good structure and organization"
        ]
    
    # Create analysis result
    result = {
        "id": len(analysis_results) + 1,
        "policy_id": policy_id,
        "analysis_type": analysis_type,
        "summary": f"This {policy['type']} outlines the company's commitments, user rights, and operational procedures.",
        "compliance": compliance,
        "readability": "Grade 12 - College level",
        "insights": insights,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    analysis_results.append(result)
    
    return result

@app.get("/analysis/{analysis_id}", response_model=AnalysisResult)
def get_analysis_result(analysis_id: int, current_user: dict = Depends(get_current_user)):
    for result in analysis_results:
        if result["id"] == analysis_id:
            # Check if the user owns the related policy
            for policy in policies:
                if policy["id"] == result["policy_id"] and policy["user_id"] == current_user["id"]:
                    return result
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Analysis result not found"
    )

@app.get("/dashboard/stats")
def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    user_policies = [p for p in policies if p["user_id"] == current_user["id"]]
    user_analyses = []
    
    for result in analysis_results:
        for policy in policies:
            if policy["id"] == result["policy_id"] and policy["user_id"] == current_user["id"]:
                user_analyses.append(result)
    
    # Calculate average compliance score (mock data)
    avg_compliance = 85
    
    return {
        "total_policies": len(user_policies),
        "total_analyses": len(user_analyses),
        "avg_compliance_score": f"{avg_compliance}%",
        "recent_activities": [
            {"type": "upload", "policy_name": p["name"], "date": p["upload_date"]}
            for p in sorted(user_policies, key=lambda x: x["upload_date"], reverse=True)[:3]
        ]
    }

@app.put("/users/api-keys")
def update_api_keys(
    openai_key: Optional[str] = Body(None),
    anthropic_key: Optional[str] = Body(None),
    current_user: dict = Depends(get_current_user)
):
    # In a real app, store these securely for the specific user
    # Here we're just returning a success message
    
    return {"message": "API keys updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
