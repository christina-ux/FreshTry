from fastapi import APIRouter, Depends, Request, Response, status
import os
import time
import logging
import psutil
import platform
from typing import Dict, Any
from datetime import datetime

from utils.health_check import HealthCheck

router = APIRouter(tags=["health"])
logger = logging.getLogger("health")

# Initialize the health check system
health_checker = HealthCheck()

# Register data directories
for data_dir in [
    "data/uploads", 
    "data/reports", 
    "data/dashboard", 
    "data/scoring", 
    "data/uploads/processed"
]:
    health_checker.check_storage(data_dir)

# Register health check for any external services used by the application
# Example: health_checker.check_external_service("openai", "https://api.openai.com/v1", critical=False)

@router.get("/health", summary="Basic health check")
async def health():
    """
    Basic health check endpoint that returns 200 OK if the API is running.
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@router.get("/health/detailed", summary="Detailed health check")
async def detailed_health():
    """
    Detailed health check that verifies all system components.
    """
    start_time = time.time()
    health_results = health_checker.run_checks()
    
    # Add system information
    system_info = {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "uptime": time.time() - psutil.boot_time(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "process_uptime": time.time() - psutil.Process().create_time(),
        "process_memory": psutil.Process().memory_info().rss / (1024 * 1024),  # MB
    }
    
    # Add environment information (be careful not to leak secrets)
    env_info = {
        "app_env": os.environ.get("APP_ENV", "unknown"),
        "build_version": os.environ.get("BUILD_VERSION", "unknown"),
        "log_level": os.environ.get("LOG_LEVEL", "unknown"),
    }
    
    result = {
        "status": health_results["status"],
        "timestamp": datetime.now().isoformat(),
        "duration_ms": int((time.time() - start_time) * 1000),
        "components": health_results["components"],
        "summary": {
            "passing": health_results["passing"],
            "total": health_results["total"],
            "critical_passing": health_results["critical_passing"],
            "critical_total": health_results["critical_total"],
        },
        "system": system_info,
        "environment": env_info,
    }
    
    return result

@router.get("/readiness", summary="Readiness probe for Kubernetes")
async def readiness(response: Response):
    """
    Readiness probe for Kubernetes/ECS.
    Returns 200 if the application is ready to receive traffic.
    """
    health_results = health_checker.run_checks()
    
    if health_results["status"] == "healthy":
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "timestamp": datetime.now().isoformat(),
            "reason": "Critical health checks failing"
        }
        
@router.get("/liveness", summary="Liveness probe for Kubernetes")
async def liveness():
    """
    Liveness probe for Kubernetes/ECS.
    Simply checks if the application is running.
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }