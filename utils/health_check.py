import logging
import time
import sys
import os
from typing import Dict, Any, List, Optional, Callable
from .api_client import APIClient

logger = logging.getLogger("health_check")

class HealthCheck:
    """Comprehensive health check system for all service components"""
    
    def __init__(self):
        self.components = {}
        self.results = {}
    
    def register_component(self, name: str, check_func: Callable[[], bool], 
                          critical: bool = False, dependencies: Optional[List[str]] = None):
        """Register a component to be health-checked"""
        self.components[name] = {
            "check_func": check_func,
            "critical": critical,
            "dependencies": dependencies or []
        }
    
    def check_api(self, endpoint: str, critical: bool = True) -> None:
        """Register an API endpoint health check"""
        api_client = APIClient(os.environ.get("API_URL", "http://localhost:8000"))
        
        def _check_api():
            try:
                return api_client.health_check(endpoint)
            except Exception as e:
                logger.error(f"API health check failed for {endpoint}: {e}")
                return False
        
        self.register_component(f"api_{endpoint}", _check_api, critical=critical)
    
    def check_database(self, connection_string: str, critical: bool = True) -> None:
        """Register a database health check"""
        # Implementation would depend on your database library
        pass
    
    def check_storage(self, path: str, critical: bool = True) -> None:
        """Register a storage health check"""
        def _check_storage():
            try:
                if not os.path.exists(path):
                    logger.error(f"Storage path does not exist: {path}")
                    return False
                    
                # Check if directory is writable
                if os.path.isdir(path):
                    test_file = os.path.join(path, ".health_check_test")
                    try:
                        with open(test_file, "w") as f:
                            f.write("test")
                        os.remove(test_file)
                        return True
                    except Exception as e:
                        logger.error(f"Storage path is not writable: {path} - {e}")
                        return False
                        
                return True
            except Exception as e:
                logger.error(f"Storage health check failed: {e}")
                return False
        
        self.register_component(f"storage_{path}", _check_storage, critical=critical)
    
    def check_external_service(self, name: str, url: str, critical: bool = False) -> None:
        """Register an external service health check"""
        api_client = APIClient()
        
        def _check_service():
            try:
                response = api_client.get(url, timeout=5)
                return True
            except Exception as e:
                logger.error(f"External service {name} health check failed: {e}")
                return False
        
        self.register_component(f"external_{name}", _check_service, critical=critical)
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        self.results = {}
        all_critical_passing = True
        
        # Sort components by dependencies
        checked_components = set()
        
        while len(checked_components) < len(self.components):
            for name, component in self.components.items():
                if name in checked_components:
                    continue
                    
                # Skip if dependencies haven't been checked yet
                if any(dep not in checked_components for dep in component["dependencies"]):
                    continue
                    
                # Skip if dependencies failed and this depends on them
                if any(dep in component["dependencies"] and not self.results.get(dep, {}).get("passing", False) 
                       for dep in self.results):
                    self.results[name] = {
                        "passing": False,
                        "error": "Dependency check failed",
                        "critical": component["critical"],
                        "time": time.time()
                    }
                else:
                    # Run the check
                    start_time = time.time()
                    try:
                        passing = component["check_func"]()
                    except Exception as e:
                        logger.error(f"Health check for {name} raised exception: {e}")
                        passing = False
                        error = str(e)
                    else:
                        error = None if passing else "Check failed"
                        
                    self.results[name] = {
                        "passing": passing,
                        "error": error,
                        "critical": component["critical"],
                        "time": time.time() - start_time
                    }
                    
                    # Update critical status
                    if component["critical"] and not passing:
                        all_critical_passing = False
                        
                checked_components.add(name)
        
        # Aggregate results
        total_checks = len(self.results)
        passing_checks = sum(1 for r in self.results.values() if r["passing"])
        critical_checks = sum(1 for r in self.results.values() if r["critical"])
        passing_critical = sum(1 for r in self.results.values() if r["passing"] and r["critical"])
        
        overall_result = {
            "status": "healthy" if all_critical_passing else "unhealthy",
            "passing": passing_checks,
            "total": total_checks,
            "critical_passing": passing_critical,
            "critical_total": critical_checks,
            "timestamp": time.time(),
            "components": self.results
        }
        
        return overall_result
    
    def check_and_exit_on_failure(self):
        """Run health checks and exit with non-zero code on critical failure"""
        results = self.run_checks()
        
        if results["status"] == "unhealthy":
            logger.error("Critical health check failed")
            for name, result in results["components"].items():
                if result["critical"] and not result["passing"]:
                    logger.error(f"Critical component {name} failed: {result['error']}")
            sys.exit(1)
            
        logger.info(f"Health check passed: {results['passing']}/{results['total']} components healthy")
        return results