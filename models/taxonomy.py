"""
Data taxonomy models for unified classification of assets, financial data,
contracts, and regulatory mappings in PolicyEdgeAI.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import date, datetime


class AssetType(str, Enum):
    """Types of assets in the organization."""
    ENDPOINT = "endpoint"
    SERVER = "server"
    NETWORK_DEVICE = "network_device"
    MOBILE_DEVICE = "mobile_device"
    CLOUD_SERVICE = "cloud_service"
    APPLICATION = "application"
    DATABASE = "database"
    VIRTUAL_MACHINE = "virtual_machine"
    CONTAINER = "container"
    IOT_DEVICE = "iot_device"
    OTHER = "other"


class AssetCategory(str, Enum):
    """Business categories for assets."""
    IT = "it"
    INFRA = "infrastructure"
    SECURITY = "security"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"
    FINANCE = "finance"
    HR = "human_resources"
    LEGAL = "legal"
    MARKETING = "marketing"
    SALES = "sales"
    OPERATIONS = "operations"
    RESEARCH = "research"
    EXECUTIVE = "executive"
    OTHER = "other"


class AssetStatus(str, Enum):
    """Operational status of assets."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"
    RESERVED = "reserved"
    STOLEN = "stolen"
    LOST = "lost"
    DISPOSED = "disposed"


class DataClassification(str, Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(str, Enum):
    """Compliance status levels."""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"
    PENDING_ASSESSMENT = "pending_assessment"


class LicenseType(str, Enum):
    """Types of software licenses."""
    PERPETUAL = "perpetual"
    SUBSCRIPTION = "subscription"
    ENTERPRISE = "enterprise"
    VOLUME = "volume"
    OPEN_SOURCE = "open_source"
    FREEWARE = "freeware"
    TRIAL = "trial"
    OEM = "oem"
    CUSTOM = "custom"


class RenewalType(str, Enum):
    """Types of contract renewal."""
    AUTO = "automatic"
    MANUAL = "manual"
    CONDITIONAL = "conditional"
    NON_RENEWABLE = "non_renewable"


class AssetData(BaseModel):
    """Asset taxonomy model for unified asset data."""
    asset_id: str = Field(..., description="Unique identifier for the asset")
    name: Optional[str] = Field(None, description="Descriptive name of the asset")
    type: AssetType = Field(..., description="Type of asset")
    source: str = Field(..., description="Source system that provided this asset information")
    owner: Optional[str] = Field(None, description="Business owner or responsible group")
    category: Optional[AssetCategory] = Field(None, description="Business category for the asset")
    status: Optional[AssetStatus] = Field(None, description="Current operational status")
    ip_addresses: Optional[List[str]] = Field(None, description="IP addresses associated with the asset")
    hostname: Optional[str] = Field(None, description="Hostname of the asset")
    os: Optional[str] = Field(None, description="Operating system of the asset")
    os_version: Optional[str] = Field(None, description="Operating system version")
    location: Optional[str] = Field(None, description="Physical or logical location")
    department: Optional[str] = Field(None, description="Department that owns the asset")
    data_classification: Optional[DataClassification] = Field(None, description="Highest classification of data processed")
    risk_level: Optional[RiskLevel] = Field(None, description="Risk level assessment")
    acquisition_date: Optional[date] = Field(None, description="Date the asset was acquired")
    last_updated: Optional[datetime] = Field(None, description="Last time the asset information was updated")
    tags: Optional[List[str]] = Field(None, description="Custom tags for the asset")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional source-specific metadata")

    class Config:
        schema_extra = {
            "example": {
                "asset_id": "ASSET-001",
                "name": "Primary Web Server",
                "type": "server",
                "source": "ServiceNow CMDB",
                "owner": "Web Operations Team",
                "category": "production",
                "status": "active",
                "ip_addresses": ["10.0.0.1", "192.168.1.1"],
                "hostname": "web-prod-01",
                "os": "Ubuntu Linux",
                "os_version": "20.04 LTS",
                "location": "Primary Data Center",
                "department": "IT Operations",
                "data_classification": "internal",
                "risk_level": "high",
                "acquisition_date": "2022-03-15",
                "last_updated": "2023-04-10T14:30:15",
                "tags": ["web", "production", "external"]
            }
        }


class FinancialData(BaseModel):
    """Financial taxonomy model for unified financial data."""
    asset_id: str = Field(..., description="Unique identifier for the associated asset")
    cost: float = Field(..., description="Cost of the asset")
    cost_currency: str = Field("USD", description="Currency for the cost value")
    acquisition_cost: Optional[float] = Field(None, description="Initial acquisition cost")
    maintenance_cost: Optional[float] = Field(None, description="Annual maintenance cost")
    depreciation_value: Optional[float] = Field(None, description="Current depreciated value")
    vendor: str = Field(..., description="Vendor or supplier name")
    vendor_id: Optional[str] = Field(None, description="Vendor identifier in procurement system")
    purchase_order: Optional[str] = Field(None, description="Associated purchase order number")
    cost_center: Optional[str] = Field(None, description="Cost center charged for this asset")
    budget_code: Optional[str] = Field(None, description="Budget code for accounting purposes")
    license_type: Optional[LicenseType] = Field(None, description="Type of license if applicable")
    license_count: Optional[int] = Field(None, description="Number of licenses if applicable")
    license_metric: Optional[str] = Field(None, description="License metric (e.g., per user, per core)")
    fiscal_year: Optional[int] = Field(None, description="Fiscal year of acquisition")
    depreciation_schedule: Optional[str] = Field(None, description="Depreciation schedule type")
    last_financial_review: Optional[date] = Field(None, description="Date of last financial review")
    notes: Optional[str] = Field(None, description="Additional financial notes")

    class Config:
        schema_extra = {
            "example": {
                "asset_id": "ASSET-001",
                "cost": 12500.00,
                "cost_currency": "USD",
                "acquisition_cost": 15000.00,
                "maintenance_cost": 2000.00,
                "depreciation_value": 8750.00,
                "vendor": "Dell Technologies",
                "vendor_id": "VNDR-0042",
                "purchase_order": "PO-2022-0789",
                "cost_center": "IT-OPS-INFRA",
                "budget_code": "CAPEX-2022-IT",
                "license_type": "perpetual",
                "fiscal_year": 2022,
                "depreciation_schedule": "5-year straight line",
                "last_financial_review": "2023-01-15"
            }
        }


class ContractData(BaseModel):
    """Contract taxonomy model for unified contract data."""
    asset_id: str = Field(..., description="Unique identifier for the associated asset")
    contract_id: str = Field(..., description="Unique identifier for the contract")
    contract_name: Optional[str] = Field(None, description="Name or title of the contract")
    expiration_date: date = Field(..., description="Expiration date of the contract")
    start_date: Optional[date] = Field(None, description="Start date of the contract")
    renewal_type: Optional[RenewalType] = Field(None, description="Type of renewal for the contract")
    renewal_terms: Optional[str] = Field(None, description="Description of renewal terms")
    renewal_notice_days: Optional[int] = Field(None, description="Days notice required for renewal/cancellation")
    auto_renewal_date: Optional[date] = Field(None, description="Date of automatic renewal if applicable")
    contract_value: Optional[float] = Field(None, description="Total value of the contract")
    monthly_cost: Optional[float] = Field(None, description="Monthly cost if applicable")
    annual_cost: Optional[float] = Field(None, description="Annual cost if applicable")
    contract_owner: Optional[str] = Field(None, description="Person responsible for the contract")
    vendor_contact: Optional[str] = Field(None, description="Vendor contact information")
    contract_type: Optional[str] = Field(None, description="Type of contract")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    cancellation_terms: Optional[str] = Field(None, description="Cancellation terms")
    document_location: Optional[str] = Field(None, description="Where the contract document is stored")
    notes: Optional[str] = Field(None, description="Additional contract notes")

    class Config:
        schema_extra = {
            "example": {
                "asset_id": "ASSET-001",
                "contract_id": "CONT-2022-0456",
                "contract_name": "Web Server Support Agreement",
                "expiration_date": "2025-03-14",
                "start_date": "2022-03-15",
                "renewal_type": "automatic",
                "renewal_terms": "Yearly renewal with 3% price increase cap",
                "renewal_notice_days": 60,
                "auto_renewal_date": "2025-03-15",
                "contract_value": 35000.00,
                "annual_cost": 12000.00,
                "contract_owner": "Jane Smith",
                "vendor_contact": "support@vendorcompany.com",
                "contract_type": "support",
                "payment_terms": "Annual, Net 30",
                "cancellation_terms": "60 days written notice, early termination fee applies",
                "document_location": "Legal Document Repository ID: DOC-5678"
            }
        }


class ControlEvidence(BaseModel):
    """Evidence supporting compliance with a regulatory control."""
    evidence_id: str = Field(..., description="Unique identifier for the evidence")
    description: str = Field(..., description="Description of the evidence")
    evidence_type: str = Field(..., description="Type of evidence (document, screenshot, report)")
    collection_date: Optional[date] = Field(None, description="Date the evidence was collected")
    collected_by: Optional[str] = Field(None, description="Person who collected the evidence")
    document_location: Optional[str] = Field(None, description="Where the evidence is stored")
    review_status: Optional[str] = Field(None, description="Review status of the evidence")
    review_notes: Optional[str] = Field(None, description="Notes from evidence review")

    class Config:
        schema_extra = {
            "example": {
                "evidence_id": "EVID-AC1-001",
                "description": "Access Control Policy document with approval signatures",
                "evidence_type": "document",
                "collection_date": "2023-02-15",
                "collected_by": "John Doe",
                "document_location": "Compliance Repository ID: AC-POLICY-V3",
                "review_status": "approved",
                "review_notes": "Policy meets all requirements for AC-1"
            }
        }


class RegulatoryMapping(BaseModel):
    """Mapping between regulatory controls and organizational assets."""
    control_id: str = Field(..., description="Identifier for the regulatory control")
    control_framework: Optional[str] = Field(None, description="Framework the control belongs to")
    related_assets: List[str] = Field(..., description="Assets related to this control")
    implementation_status: Optional[ComplianceStatus] = Field(None, description="Status of control implementation")
    implementation_date: Optional[date] = Field(None, description="Date of implementation")
    last_assessment_date: Optional[date] = Field(None, description="Date of last assessment")
    next_assessment_date: Optional[date] = Field(None, description="Date of next scheduled assessment")
    responsible_party: Optional[str] = Field(None, description="Person or team responsible for the control")
    risk_rating: Optional[RiskLevel] = Field(None, description="Risk level if not implemented")
    evidence: Optional[List[ControlEvidence]] = Field(None, description="Evidence of compliance")
    notes: Optional[str] = Field(None, description="Additional notes about the mapping")

    class Config:
        schema_extra = {
            "example": {
                "control_id": "AC-2",
                "control_framework": "NIST 800-53",
                "related_assets": ["ASSET-001", "ASSET-002", "ASSET-003"],
                "implementation_status": "compliant",
                "implementation_date": "2022-06-30",
                "last_assessment_date": "2023-01-15",
                "next_assessment_date": "2023-07-15",
                "responsible_party": "Identity Management Team",
                "risk_rating": "high",
                "evidence": [
                    {
                        "evidence_id": "EVID-AC2-001",
                        "description": "Account management procedures document",
                        "evidence_type": "document",
                        "collection_date": "2023-01-15",
                        "collected_by": "Jane Smith",
                        "document_location": "Compliance Repository ID: AC2-PROC-V2",
                        "review_status": "approved"
                    }
                ],
                "notes": "Control implementation verified through automated account management workflow"
            }
        }


class ScoringMetric(BaseModel):
    """Metric used for calculating compliance scores."""
    metric_id: str = Field(..., description="Unique identifier for the metric")
    name: str = Field(..., description="Name of the metric")
    description: str = Field(..., description="Description of what the metric measures")
    weight: float = Field(..., description="Weight of this metric in the overall score (0-1)")
    calculation_method: str = Field(..., description="Method used to calculate this metric")
    target_value: Optional[float] = Field(None, description="Target value for this metric")
    threshold_warning: Optional[float] = Field(None, description="Threshold for warning level")
    threshold_critical: Optional[float] = Field(None, description="Threshold for critical level")

    class Config:
        schema_extra = {
            "example": {
                "metric_id": "METRIC-001",
                "name": "Control Implementation Rate",
                "description": "Percentage of applicable controls that are fully implemented",
                "weight": 0.3,
                "calculation_method": "implemented_controls / applicable_controls * 100",
                "target_value": 95.0,
                "threshold_warning": 85.0,
                "threshold_critical": 75.0
            }
        }


class ComplianceScore(BaseModel):
    """Compliance score for a framework or organization."""
    score_id: str = Field(..., description="Unique identifier for the score")
    framework: Optional[str] = Field(None, description="Framework being scored (if applicable)")
    score_date: date = Field(..., description="Date the score was calculated")
    overall_score: float = Field(..., description="Overall compliance score (0-100)")
    metrics: List[Dict[str, Any]] = Field(..., description="Metrics used in calculation")
    previous_score: Optional[float] = Field(None, description="Previous overall score for comparison")
    trend: Optional[str] = Field(None, description="Trend direction (improving, declining, stable)")
    notes: Optional[str] = Field(None, description="Additional notes about the score")

    class Config:
        schema_extra = {
            "example": {
                "score_id": "SCORE-NIST-2023Q1",
                "framework": "NIST 800-53",
                "score_date": "2023-03-31",
                "overall_score": 87.3,
                "metrics": [
                    {
                        "metric_id": "METRIC-001",
                        "name": "Control Implementation Rate",
                        "value": 92.5,
                        "weight": 0.3,
                        "weighted_score": 27.75
                    },
                    {
                        "metric_id": "METRIC-002",
                        "name": "Evidence Quality",
                        "value": 85.0,
                        "weight": 0.2,
                        "weighted_score": 17.0
                    }
                ],
                "previous_score": 84.1,
                "trend": "improving",
                "notes": "Significant improvement in control implementation rate this quarter"
            }
        }


class UserFeedback(BaseModel):
    """User feedback on the compliance tooling and processes."""
    feedback_id: str = Field(..., description="Unique identifier for the feedback")
    user_id: str = Field(..., description="Identifier for the user providing feedback")
    feedback_date: datetime = Field(..., description="Date and time the feedback was provided")
    feedback_type: str = Field(..., description="Type of feedback (suggestion, issue, praise)")
    feature: str = Field(..., description="Feature or area the feedback relates to")
    satisfaction_rating: Optional[int] = Field(None, description="Satisfaction rating (1-5)")
    usability_rating: Optional[int] = Field(None, description="Usability rating (1-5)")
    feedback_text: str = Field(..., description="Detailed feedback text")
    resolution_status: Optional[str] = Field(None, description="Status of feedback resolution")
    resolution_notes: Optional[str] = Field(None, description="Notes about the resolution")

    class Config:
        schema_extra = {
            "example": {
                "feedback_id": "FB-2023-042",
                "user_id": "user.smith",
                "feedback_date": "2023-03-15T14:22:30",
                "feedback_type": "suggestion",
                "feature": "regulatory mapping",
                "satisfaction_rating": 4,
                "usability_rating": 3,
                "feedback_text": "The evidence upload feature is useful but would benefit from batch upload capability.",
                "resolution_status": "planned",
                "resolution_notes": "Batch upload planned for Q3 2023 release"
            }
        }