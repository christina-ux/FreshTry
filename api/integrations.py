"""
API integrations with external enterprise systems.

This module provides integration endpoints for various IT management, security,
and compliance tools, allowing PolicyEdgeAI to fetch and correlate data from
multiple sources.
"""
import os
import logging
import json
from typing import Dict, List, Any, Optional
import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create router
integrations = APIRouter(
    prefix="/api/integrations",
    tags=["integrations"],
    responses={404: {"description": "Integration not found"}},
)


# Model for integrations configuration
class IntegrationConfig(BaseModel):
    """Configuration for an external integration."""
    name: str
    base_url: str
    auth_type: str  # "basic", "oauth", "api_key", "none"
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    oauth_token: Optional[str] = None
    headers: Dict[str, str] = {}
    enabled: bool = True


class IntegrationManager:
    """Manages connections to external systems."""
    
    def __init__(self):
        """Initialize integration manager."""
        self.configs = {}
        self.load_configs()
    
    def load_configs(self):
        """Load integration configurations from environment or config file."""
        # Load from config file if available
        config_path = os.path.join(os.getcwd(), "data", "integrations", "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    configs = json.load(f)
                    
                for name, config in configs.items():
                    self.configs[name] = IntegrationConfig(**config)
                    
                logger.info(f"Loaded {len(self.configs)} integration configurations from file")
            except Exception as e:
                logger.error(f"Error loading integration configurations: {str(e)}")
        
        # Initialize default configurations if not loaded
        if not self.configs:
            self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default integration configurations."""
        # ServiceNow CMDB
        self.configs["servicenow_cmdb"] = IntegrationConfig(
            name="ServiceNow CMDB",
            base_url=os.getenv("SERVICENOW_URL", "https://instance.service-now.com"),
            auth_type="basic",
            username=os.getenv("SERVICENOW_USERNAME", ""),
            password=os.getenv("SERVICENOW_PASSWORD", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_SERVICENOW", "false").lower() == "true")
        )
        
        # ServiceNow SAM Pro
        self.configs["servicenow_sampro"] = IntegrationConfig(
            name="ServiceNow SAM Pro",
            base_url=os.getenv("SERVICENOW_URL", "https://instance.service-now.com"),
            auth_type="basic",
            username=os.getenv("SERVICENOW_USERNAME", ""),
            password=os.getenv("SERVICENOW_PASSWORD", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_SERVICENOW", "false").lower() == "true")
        )
        
        # Category Management Tools
        self.configs["category_mgmt"] = IntegrationConfig(
            name="Category Management Tools",
            base_url=os.getenv("CATEGORY_MGMT_URL", "https://api.category-mgmt.gov"),
            auth_type="api_key",
            api_key=os.getenv("CATEGORY_MGMT_API_KEY", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_CATEGORY_MGMT", "false").lower() == "true")
        )
        
        # BigFix
        self.configs["bigfix"] = IntegrationConfig(
            name="BigFix",
            base_url=os.getenv("BIGFIX_URL", "https://bigfix.example.com/api"),
            auth_type="basic",
            username=os.getenv("BIGFIX_USERNAME", ""),
            password=os.getenv("BIGFIX_PASSWORD", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_BIGFIX", "false").lower() == "true")
        )
        
        # CrowdStrike
        self.configs["crowdstrike"] = IntegrationConfig(
            name="CrowdStrike",
            base_url=os.getenv("CROWDSTRIKE_URL", "https://api.crowdstrike.com"),
            auth_type="oauth",
            oauth_token=os.getenv("CROWDSTRIKE_TOKEN", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_CROWDSTRIKE", "false").lower() == "true")
        )
        
        # Splunk
        self.configs["splunk"] = IntegrationConfig(
            name="Splunk",
            base_url=os.getenv("SPLUNK_URL", "https://splunk.example.com/services/search/jobs"),
            auth_type="basic",
            username=os.getenv("SPLUNK_USERNAME", ""),
            password=os.getenv("SPLUNK_PASSWORD", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_SPLUNK", "false").lower() == "true")
        )
        
        # Qualys
        self.configs["qualys"] = IntegrationConfig(
            name="Qualys",
            base_url=os.getenv("QUALYS_URL", "https://qualysapi.qualys.com/api/2.0"),
            auth_type="basic",
            username=os.getenv("QUALYS_USERNAME", ""),
            password=os.getenv("QUALYS_PASSWORD", ""),
            headers={"Accept": "application/xml"},
            enabled=bool(os.getenv("ENABLE_QUALYS", "false").lower() == "true")
        )
        
        # Tenable
        self.configs["tenable"] = IntegrationConfig(
            name="Tenable",
            base_url=os.getenv("TENABLE_URL", "https://cloud.tenable.com"),
            auth_type="api_key",
            api_key=os.getenv("TENABLE_API_KEY", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_TENABLE", "false").lower() == "true")
        )
        
        # Jamf
        self.configs["jamf"] = IntegrationConfig(
            name="Jamf",
            base_url=os.getenv("JAMF_URL", "https://jamf.example.com/JSSResource"),
            auth_type="basic",
            username=os.getenv("JAMF_USERNAME", ""),
            password=os.getenv("JAMF_PASSWORD", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_JAMF", "false").lower() == "true")
        )
        
        # Intune
        self.configs["intune"] = IntegrationConfig(
            name="Intune",
            base_url=os.getenv("INTUNE_URL", "https://graph.microsoft.com/v1.0/deviceManagement"),
            auth_type="oauth",
            oauth_token=os.getenv("MICROSOFT_TOKEN", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_INTUNE", "false").lower() == "true")
        )
        
        # Azure AD
        self.configs["azure_ad"] = IntegrationConfig(
            name="Azure AD",
            base_url=os.getenv("AZURE_AD_URL", "https://graph.microsoft.com/v1.0/users"),
            auth_type="oauth",
            oauth_token=os.getenv("MICROSOFT_TOKEN", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_AZURE_AD", "false").lower() == "true")
        )
        
        # Axonius
        self.configs["axonius"] = IntegrationConfig(
            name="Axonius",
            base_url=os.getenv("AXONIUS_URL", "https://axonius.example.com/api/v1"),
            auth_type="api_key",
            api_key=os.getenv("AXONIUS_API_KEY", ""),
            headers={"Accept": "application/json"},
            enabled=bool(os.getenv("ENABLE_AXONIUS", "false").lower() == "true")
        )
        
        logger.info(f"Initialized {len(self.configs)} default integration configurations")
    
    def get_config(self, name):
        """Get configuration for a specific integration."""
        if name not in self.configs:
            raise ValueError(f"Integration '{name}' not configured")
        
        return self.configs[name]
    
    def list_integrations(self):
        """List all configured integrations."""
        return [{"name": name, "enabled": config.enabled} for name, config in self.configs.items()]
    
    def get_headers(self, config):
        """Get headers for a specific integration, including authentication."""
        headers = config.headers.copy()
        
        if config.auth_type == "basic":
            import base64
            if config.username and config.password:
                auth_string = f"{config.username}:{config.password}"
                encoded_auth = base64.b64encode(auth_string.encode()).decode()
                headers["Authorization"] = f"Basic {encoded_auth}"
        elif config.auth_type == "oauth":
            if config.oauth_token:
                headers["Authorization"] = f"Bearer {config.oauth_token}"
        elif config.auth_type == "api_key":
            if config.api_key:
                headers["X-API-Key"] = config.api_key
        
        return headers
    
    def make_request(self, integration_name, endpoint="", method="GET", params=None, data=None):
        """Make a request to an integration."""
        if integration_name not in self.configs:
            raise ValueError(f"Integration '{integration_name}' not configured")
        
        config = self.configs[integration_name]
        
        if not config.enabled:
            raise ValueError(f"Integration '{integration_name}' is not enabled")
        
        # Build URL
        url = f"{config.base_url}/{endpoint}".rstrip("/")
        
        # Get headers with authentication
        headers = self.get_headers(config)
        
        try:
            # Make request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data if method in ["POST", "PUT", "PATCH"] and data else None
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            elif "application/xml" in content_type:
                # Return XML as string - the caller can parse it if needed
                return {"xml_content": response.text}
            else:
                return {"content": response.text}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {integration_name}: {str(e)}")
            # In production, you might want to handle specific error cases differently
            raise ValueError(f"Error communicating with {integration_name}: {str(e)}")


# Create integration manager instance
integration_manager = IntegrationManager()


# Dependency to get integration manager
def get_integration_manager():
    return integration_manager


# Endpoints for ServiceNow CMDB
@integrations.get("/cmdb/servicenow", summary="Get ServiceNow CMDB data")
async def get_servicenow_cmdb(
    limit: int = Query(100, description="Maximum number of records to return"),
    offset: int = Query(0, description="Offset for pagination"),
    query: Optional[str] = Query(None, description="Query string to filter results"),
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get Configuration Items (CIs) from ServiceNow CMDB.
    
    This endpoint connects to ServiceNow CMDB to retrieve configuration items,
    which can be used for asset inventory and compliance mapping.
    """
    try:
        params = {
            "sysparm_limit": limit,
            "sysparm_offset": offset,
            "sysparm_display_value": "true"
        }
        
        if query:
            params["sysparm_query"] = query
        
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request(
                "servicenow_cmdb", 
                endpoint="api/now/table/cmdb_ci",
                params=params
            )
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "result": [
                    {
                        "sys_id": "1234567890abcdef1234567890abcdef",
                        "name": "app-server-001",
                        "sys_class_name": "cmdb_ci_linux_server",
                        "os": "Linux",
                        "os_version": "Ubuntu 20.04",
                        "ip_address": "10.0.0.1",
                        "status": "Operational"
                    },
                    {
                        "sys_id": "234567890abcdef1234567890abcdef1",
                        "name": "db-server-001",
                        "sys_class_name": "cmdb_ci_db_mssql_instance",
                        "os": "Windows",
                        "os_version": "Windows Server 2019",
                        "ip_address": "10.0.0.2",
                        "status": "Operational"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting ServiceNow CMDB data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for ServiceNow SAM Pro
@integrations.get("/sampro/servicenow", summary="Get ServiceNow Software Asset Management data")
async def get_servicenow_sampro(
    limit: int = Query(100, description="Maximum number of records to return"),
    offset: int = Query(0, description="Offset for pagination"),
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get software asset data from ServiceNow Software Asset Management.
    
    This endpoint connects to ServiceNow SAM Pro to retrieve software assets,
    which can be used for license compliance and software inventory.
    """
    try:
        params = {
            "sysparm_limit": limit,
            "sysparm_offset": offset,
            "sysparm_display_value": "true"
        }
        
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request(
                "servicenow_sampro", 
                endpoint="api/now/table/cmdb_software_instance",
                params=params
            )
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "software_assets": [
                    {
                        "id": "SW001",
                        "name": "Microsoft Office 365",
                        "version": "2022",
                        "license_count": 500,
                        "used_licenses": 423,
                        "status": "Active"
                    },
                    {
                        "id": "SW002",
                        "name": "Adobe Creative Cloud",
                        "version": "2023",
                        "license_count": 100,
                        "used_licenses": 87,
                        "status": "Active"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting ServiceNow SAM Pro data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for Category Management Tools
@integrations.get("/categorymgmt/tools", summary="Get Category Management Tools data")
async def get_category_management_tools(
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get category management data for federal procurement.
    
    This endpoint connects to Category Management Tools to retrieve
    category information for federal procurement and compliance.
    """
    try:
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request("category_mgmt", endpoint="categories")
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "categories": [
                    {
                        "id": "CAT001",
                        "name": "Information Technology",
                        "subcategories": [
                            "Security Software",
                            "Cloud Computing",
                            "Network Equipment"
                        ],
                        "status": "Active"
                    },
                    {
                        "id": "CAT002",
                        "name": "Professional Services",
                        "subcategories": [
                            "Consulting",
                            "Training",
                            "Technical Support"
                        ],
                        "status": "Active"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting Category Management Tools data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for BigFix
@integrations.get("/bigfix/devices", summary="Get BigFix device inventory")
async def get_bigfix_inventory(
    limit: int = Query(100, description="Maximum number of records to return"),
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get device inventory from BigFix.
    
    This endpoint connects to BigFix to retrieve device inventory information,
    which can be used for compliance checking and vulnerability management.
    """
    try:
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request(
                "bigfix", 
                endpoint="devices",
                params={"limit": limit}
            )
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "devices": [
                    {
                        "id": "BF001",
                        "hostname": "laptop-user1",
                        "os": "Windows 10",
                        "ip_address": "192.168.1.101",
                        "last_report_time": "2023-05-15T14:32:10Z",
                        "compliance_status": "Compliant"
                    },
                    {
                        "id": "BF002",
                        "hostname": "desktop-user2",
                        "os": "Windows 11",
                        "ip_address": "192.168.1.102",
                        "last_report_time": "2023-05-15T12:15:22Z",
                        "compliance_status": "Non-Compliant"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting BigFix inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for CrowdStrike
@integrations.get("/crowdstrike/assets", summary="Get CrowdStrike asset information")
async def get_crowdstrike_assets(
    limit: int = Query(100, description="Maximum number of records to return"),
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get asset information from CrowdStrike.
    
    This endpoint connects to CrowdStrike to retrieve asset information,
    which can be used for security compliance and threat management.
    """
    try:
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request(
                "crowdstrike", 
                endpoint="devices/queries/devices/v1",
                params={"limit": limit}
            )
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "assets": [
                    {
                        "id": "CS001",
                        "hostname": "workstation-finance1",
                        "os": "Windows 10",
                        "last_seen": "2023-05-15T23:12:45Z",
                        "status": "Online",
                        "policies": ["Default", "PCI-DSS"]
                    },
                    {
                        "id": "CS002",
                        "hostname": "server-hr1",
                        "os": "Windows Server 2019",
                        "last_seen": "2023-05-15T23:10:12Z",
                        "status": "Online",
                        "policies": ["Default", "HIPAA"]
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting CrowdStrike assets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for Splunk
@integrations.get("/splunk/logs", summary="Get Splunk logs")
async def get_splunk_logs(
    query: str = Query("search index=main", description="Splunk search query"),
    limit: int = Query(100, description="Maximum number of records to return"),
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get logs from Splunk.
    
    This endpoint connects to Splunk to retrieve logs based on a search query,
    which can be used for security monitoring and compliance auditing.
    """
    try:
        # For demo purposes, return mock data if integration is not configured
        try:
            # In a real implementation, this would create a search job and get results
            data = manager.make_request(
                "splunk", 
                endpoint="search/jobs",
                method="POST",
                data={"search": query, "count": limit}
            )
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "logs": [
                    {
                        "id": "LOG001",
                        "timestamp": "2023-05-15T08:45:12.123Z",
                        "source": "firewall",
                        "source_ip": "203.0.113.10",
                        "destination_ip": "10.0.0.5",
                        "action": "blocked",
                        "reason": "Suspicious activity"
                    },
                    {
                        "id": "LOG002",
                        "timestamp": "2023-05-15T08:46:23.456Z",
                        "source": "authentication",
                        "user": "jsmith",
                        "action": "login",
                        "status": "success",
                        "location": "New York"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting Splunk logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for Qualys
@integrations.get("/qualys/assets", summary="Get Qualys asset information")
async def get_qualys_assets(
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get asset information from Qualys.
    
    This endpoint connects to Qualys to retrieve asset information,
    which can be used for vulnerability management and compliance.
    """
    try:
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request("qualys", endpoint="asset/host/list")
            # Parse XML response if needed
            if "xml_content" in data:
                # In a real implementation, you would parse the XML here
                # For now, return mock data
                return {
                    "assets": [
                        {
                            "id": "Q001",
                            "hostname": "web-server-1",
                            "ip": "10.0.0.10",
                            "os": "CentOS 7",
                            "last_scan": "2023-05-10T15:30:00Z",
                            "vulnerabilities": {
                                "critical": 0,
                                "high": 2,
                                "medium": 5,
                                "low": 12
                            }
                        },
                        {
                            "id": "Q002",
                            "hostname": "app-server-1",
                            "ip": "10.0.0.11",
                            "os": "Ubuntu 20.04",
                            "last_scan": "2023-05-11T16:45:00Z",
                            "vulnerabilities": {
                                "critical": 1,
                                "high": 3,
                                "medium": 8,
                                "low": 15
                            }
                        }
                    ]
                }
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "assets": [
                    {
                        "id": "Q001",
                        "hostname": "web-server-1",
                        "ip": "10.0.0.10",
                        "os": "CentOS 7",
                        "last_scan": "2023-05-10T15:30:00Z",
                        "vulnerabilities": {
                            "critical": 0,
                            "high": 2,
                            "medium": 5,
                            "low": 12
                        }
                    },
                    {
                        "id": "Q002",
                        "hostname": "app-server-1",
                        "ip": "10.0.0.11",
                        "os": "Ubuntu 20.04",
                        "last_scan": "2023-05-11T16:45:00Z",
                        "vulnerabilities": {
                            "critical": 1,
                            "high": 3,
                            "medium": 8,
                            "low": 15
                        }
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting Qualys assets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for Tenable
@integrations.get("/tenable/vulnerabilities", summary="Get Tenable vulnerability information")
async def get_tenable_vulns(
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get vulnerability information from Tenable.
    
    This endpoint connects to Tenable to retrieve vulnerability information,
    which can be used for security compliance and risk management.
    """
    try:
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request("tenable", endpoint="workbenches/vulnerabilities")
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "vulnerabilities": [
                    {
                        "id": "V001",
                        "plugin_id": 12345,
                        "name": "OpenSSL Heartbleed",
                        "severity": "Critical",
                        "count": 3,
                        "affected_assets": ["web-server-2", "load-balancer-1"]
                    },
                    {
                        "id": "V002",
                        "plugin_id": 23456,
                        "name": "Log4j Remote Code Execution",
                        "severity": "Critical",
                        "count": 5,
                        "affected_assets": ["app-server-3", "app-server-4", "api-gateway-1"]
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting Tenable vulnerabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for Jamf
@integrations.get("/jamf/devices", summary="Get Jamf device information")
async def get_jamf_devices(
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get device information from Jamf.
    
    This endpoint connects to Jamf to retrieve Apple device information,
    which can be used for macOS compliance and management.
    """
    try:
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request("jamf", endpoint="computers")
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "devices": [
                    {
                        "id": "J001",
                        "name": "MacBook Pro - John Smith",
                        "serial_number": "C02XL0TGJHCD",
                        "model": "MacBook Pro (16-inch, 2021)",
                        "os_version": "macOS 12.6",
                        "last_check_in": "2023-05-15T10:23:45Z",
                        "compliance_status": "Compliant"
                    },
                    {
                        "id": "J002",
                        "name": "MacBook Air - Jane Doe",
                        "serial_number": "C02CK0VWJHCX",
                        "model": "MacBook Air (13-inch, 2022)",
                        "os_version": "macOS 13.0",
                        "last_check_in": "2023-05-15T09:15:30Z",
                        "compliance_status": "Non-Compliant"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting Jamf devices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for Intune
@integrations.get("/intune/devices", summary="Get Intune device information")
async def get_intune_devices(
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get device information from Microsoft Intune.
    
    This endpoint connects to Intune to retrieve managed device information,
    which can be used for compliance and mobile device management.
    """
    try:
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request("intune", endpoint="managedDevices")
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "devices": [
                    {
                        "id": "I001",
                        "deviceName": "Surface Pro - Alice Johnson",
                        "serialNumber": "029384756",
                        "model": "Surface Pro 8",
                        "osVersion": "Windows 11",
                        "lastSyncDateTime": "2023-05-15T14:25:10Z",
                        "complianceState": "compliant"
                    },
                    {
                        "id": "I002",
                        "deviceName": "iPhone - Bob Williams",
                        "serialNumber": "A1B2C3D4E5",
                        "model": "iPhone 14",
                        "osVersion": "iOS 16.4",
                        "lastSyncDateTime": "2023-05-15T13:10:45Z",
                        "complianceState": "noncompliant"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting Intune devices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for Azure AD
@integrations.get("/azure/ad-users", summary="Get Azure AD user information")
async def get_azure_ad_users(
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get user information from Azure Active Directory.
    
    This endpoint connects to Azure AD to retrieve user information,
    which can be used for identity management and compliance.
    """
    try:
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request("azure_ad", endpoint="")
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "users": [
                    {
                        "id": "U001",
                        "userPrincipalName": "john.smith@example.com",
                        "displayName": "John Smith",
                        "jobTitle": "Software Engineer",
                        "department": "Engineering",
                        "accountEnabled": True,
                        "mfaStatus": "Enabled"
                    },
                    {
                        "id": "U002",
                        "userPrincipalName": "jane.doe@example.com",
                        "displayName": "Jane Doe",
                        "jobTitle": "IT Manager",
                        "department": "Information Technology",
                        "accountEnabled": True,
                        "mfaStatus": "Enabled"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting Azure AD users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints for Axonius
@integrations.get("/axonius/assets", summary="Get Axonius asset information")
async def get_axonius_assets(
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get asset information from Axonius.
    
    This endpoint connects to Axonius to retrieve unified asset information,
    which provides a consolidated view across multiple security tools.
    """
    try:
        # For demo purposes, return mock data if integration is not configured
        try:
            data = manager.make_request("axonius", endpoint="devices")
            return data
        except ValueError:
            # Return mock data if integration is not available
            return {
                "assets": [
                    {
                        "id": "A001",
                        "hostname": "workstation-123",
                        "adapters": ["CrowdStrike", "BigFix", "Qualys"],
                        "os": "Windows 10",
                        "ip_addresses": ["10.0.0.50", "192.168.1.50"],
                        "last_seen": "2023-05-15T20:15:30Z",
                        "tags": ["Finance", "PCI"]
                    },
                    {
                        "id": "A002",
                        "hostname": "server-456",
                        "adapters": ["CrowdStrike", "Qualys", "Tenable"],
                        "os": "Ubuntu 20.04",
                        "ip_addresses": ["10.0.0.60", "192.168.1.60"],
                        "last_seen": "2023-05-15T19:45:12Z",
                        "tags": ["IT", "Critical"]
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Error getting Axonius assets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to list all available integrations
@integrations.get("/list", summary="List all available integrations")
async def list_integrations(
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    List all available integrations.
    
    This endpoint returns a list of all configured integrations
    and their enabled status.
    """
    try:
        return {"integrations": manager.list_integrations()}
    except Exception as e:
        logger.error(f"Error listing integrations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint for unified asset search across integrations
@integrations.get("/search/assets", summary="Search assets across all integrations")
async def search_assets(
    query: str = Query(..., description="Search query"),
    integrations: List[str] = Query(None, description="Specific integrations to search (empty for all)"),
    manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Search for assets across multiple integrations.
    
    This endpoint provides a unified search capability across all enabled
    integrations, allowing you to find assets based on a search query.
    """
    try:
        # In a real implementation, this would perform parallel searches across multiple integrations
        # For demo purposes, return mock data
        return {
            "results": [
                {
                    "source": "ServiceNow CMDB",
                    "type": "server",
                    "id": "cmdb_123456",
                    "name": "web-server-1",
                    "attributes": {
                        "ip": "10.0.0.15",
                        "os": "Ubuntu 20.04",
                        "status": "Active"
                    }
                },
                {
                    "source": "CrowdStrike",
                    "type": "endpoint",
                    "id": "cs_789012",
                    "name": "workstation-dev-15",
                    "attributes": {
                        "ip": "10.0.1.25",
                        "os": "Windows 10",
                        "status": "Online"
                    }
                },
                {
                    "source": "Qualys",
                    "type": "server",
                    "id": "qualys_345678",
                    "name": "app-server-3",
                    "attributes": {
                        "ip": "10.0.2.35",
                        "os": "RHEL 8",
                        "vulnerabilities": 12
                    }
                }
            ],
            "total": 3,
            "query": query,
            "integrations_searched": integrations or "all enabled"
        }
    except Exception as e:
        logger.error(f"Error searching assets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint for unified compliance dashboard
@integrations.get("/dashboard/compliance", summary="Get unified compliance dashboard")
async def get_compliance_dashboard():
    """
    Get a unified compliance dashboard across all integrations.
    
    This endpoint provides a comprehensive compliance view aggregated
    from multiple security and management tools.
    """
    try:
        # In a real implementation, this would aggregate data from multiple sources
        # For demo purposes, return mock data
        return {
            "summary": {
                "overall_compliance_score": 83.5,
                "critical_issues": 5,
                "high_issues": 15,
                "medium_issues": 28,
                "low_issues": 42
            },
            "frameworks": [
                {
                    "name": "NIST 800-53",
                    "compliance_score": 86.2,
                    "controls_total": 325,
                    "controls_compliant": 280,
                    "controls_partial": 25,
                    "controls_non_compliant": 20
                },
                {
                    "name": "HIPAA",
                    "compliance_score": 91.5,
                    "controls_total": 75,
                    "controls_compliant": 68,
                    "controls_partial": 4,
                    "controls_non_compliant": 3
                },
                {
                    "name": "PCI-DSS",
                    "compliance_score": 79.8,
                    "controls_total": 90,
                    "controls_compliant": 72,
                    "controls_partial": 8,
                    "controls_non_compliant": 10
                }
            ],
            "assets": {
                "total": 1250,
                "compliant": 984,
                "non_compliant": 266,
                "by_type": {
                    "servers": {"total": 350, "compliant": 280},
                    "workstations": {"total": 750, "compliant": 607},
                    "network_devices": {"total": 85, "compliant": 57},
                    "mobile_devices": {"total": 65, "compliant": 40}
                }
            },
            "trend": [
                {"date": "2023-04-15", "score": 78.2},
                {"date": "2023-04-22", "score": 79.5},
                {"date": "2023-04-29", "score": 81.0},
                {"date": "2023-05-06", "score": 82.8},
                {"date": "2023-05-13", "score": 83.5}
            ]
        }
    except Exception as e:
        logger.error(f"Error getting compliance dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))