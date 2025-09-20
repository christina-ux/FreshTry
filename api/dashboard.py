"""
Dashboard API endpoints for PolicyEdgeAI.

Provides unified views of assets, financial data, contracts, regulatory mappings,
and compliance scores through a taxonomy-based data model.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any, Optional
import logging
from datetime import date, datetime, timedelta
import json
import os
from models.taxonomy import (
    AssetData, FinancialData, ContractData, RegulatoryMapping,
    ComplianceScore, ScoringMetric, UserFeedback, 
    AssetType, AssetCategory, ComplianceStatus, RiskLevel
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create router
dashboard = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Dashboard data not found"}}
)


# Mock data management class
class DashboardDataManager:
    """Manages dashboard data including assets, financials, contracts, and regulatory mappings."""
    
    def __init__(self):
        """Initialize with sample data."""
        self.data_dir = os.path.join(os.getcwd(), "data", "dashboard")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data stores
        self.assets = self._load_or_create_sample("assets.json", self._create_sample_assets)
        self.financials = self._load_or_create_sample("financials.json", self._create_sample_financials)
        self.contracts = self._load_or_create_sample("contracts.json", self._create_sample_contracts)
        self.regulatory_links = self._load_or_create_sample("regulatory.json", self._create_sample_regulatory)
        self.compliance_scores = self._load_or_create_sample("scores.json", self._create_sample_scores)
        self.scoring_metrics = self._load_or_create_sample("metrics.json", self._create_sample_metrics)
        self.user_feedback = self._load_or_create_sample("feedback.json", self._create_sample_feedback)
    
    def _load_or_create_sample(self, filename, sample_func):
        """Load data from file or create sample data if file doesn't exist."""
        file_path = os.path.join(self.data_dir, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
                return sample_func()
        else:
            data = sample_func()
            try:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            except Exception as e:
                logger.error(f"Error saving {filename}: {str(e)}")
            return data
    
    def _create_sample_assets(self):
        """Create sample asset data."""
        return [
            {
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
            },
            {
                "asset_id": "ASSET-002",
                "name": "Finance Department Workstation",
                "type": "endpoint",
                "source": "BigFix",
                "owner": "Finance Department",
                "category": "finance",
                "status": "active",
                "ip_addresses": ["10.0.5.22"],
                "hostname": "fin-ws-022",
                "os": "Windows",
                "os_version": "11 Pro",
                "location": "Finance Office",
                "department": "Finance",
                "data_classification": "confidential",
                "risk_level": "medium",
                "acquisition_date": "2021-11-20",
                "last_updated": "2023-03-28T09:15:30",
                "tags": ["finance", "windows", "endpoint"]
            },
            {
                "asset_id": "ASSET-003",
                "name": "Customer Database Server",
                "type": "server",
                "source": "Axonius",
                "owner": "Database Administration",
                "category": "production",
                "status": "active",
                "ip_addresses": ["10.0.0.5"],
                "hostname": "db-prod-01",
                "os": "Red Hat Enterprise Linux",
                "os_version": "9.0",
                "location": "Primary Data Center",
                "department": "IT Operations",
                "data_classification": "restricted",
                "risk_level": "critical",
                "acquisition_date": "2022-01-10",
                "last_updated": "2023-04-05T11:45:22",
                "tags": ["database", "customer-data", "production"]
            },
            {
                "asset_id": "ASSET-004",
                "name": "Marketing Laptop",
                "type": "endpoint",
                "source": "Jamf",
                "owner": "Marketing Team",
                "category": "marketing",
                "status": "active",
                "ip_addresses": ["10.0.8.15"],
                "hostname": "mkt-mbp-015",
                "os": "macOS",
                "os_version": "13.0",
                "location": "Marketing Department",
                "department": "Marketing",
                "data_classification": "internal",
                "risk_level": "low",
                "acquisition_date": "2022-09-05",
                "last_updated": "2023-04-01T16:20:45",
                "tags": ["marketing", "macbook", "laptop"]
            },
            {
                "asset_id": "ASSET-005",
                "name": "Network Firewall",
                "type": "network_device",
                "source": "ServiceNow CMDB",
                "owner": "Network Security Team",
                "category": "security",
                "status": "active",
                "ip_addresses": ["10.0.0.254"],
                "hostname": "fw-edge-01",
                "os": "Cisco Firepower",
                "os_version": "7.2",
                "location": "Primary Data Center",
                "department": "IT Security",
                "data_classification": "confidential",
                "risk_level": "critical",
                "acquisition_date": "2020-07-22",
                "last_updated": "2023-03-15T10:10:10",
                "tags": ["network", "security", "firewall", "edge"]
            }
        ]
    
    def _create_sample_financials(self):
        """Create sample financial data."""
        return [
            {
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
            },
            {
                "asset_id": "ASSET-002",
                "cost": 1800.00,
                "cost_currency": "USD",
                "acquisition_cost": 1800.00,
                "maintenance_cost": 0.00,
                "depreciation_value": 1200.00,
                "vendor": "Dell Technologies",
                "vendor_id": "VNDR-0042",
                "purchase_order": "PO-2021-1122",
                "cost_center": "FIN-OPS",
                "budget_code": "CAPEX-2021-FIN",
                "license_type": "oem",
                "fiscal_year": 2021,
                "depreciation_schedule": "3-year straight line",
                "last_financial_review": "2022-12-10"
            },
            {
                "asset_id": "ASSET-003",
                "cost": 45000.00,
                "cost_currency": "USD",
                "acquisition_cost": 45000.00,
                "maintenance_cost": 5000.00,
                "depreciation_value": 36000.00,
                "vendor": "IBM",
                "vendor_id": "VNDR-0018",
                "purchase_order": "PO-2022-0123",
                "cost_center": "IT-OPS-DB",
                "budget_code": "CAPEX-2022-IT",
                "license_type": "enterprise",
                "license_count": 1,
                "license_metric": "per server",
                "fiscal_year": 2022,
                "depreciation_schedule": "5-year straight line",
                "last_financial_review": "2023-01-15"
            },
            {
                "asset_id": "ASSET-004",
                "cost": 2500.00,
                "cost_currency": "USD",
                "acquisition_cost": 2500.00,
                "maintenance_cost": 0.00,
                "depreciation_value": 2000.00,
                "vendor": "Apple",
                "vendor_id": "VNDR-0008",
                "purchase_order": "PO-2022-0901",
                "cost_center": "MKT-OPS",
                "budget_code": "CAPEX-2022-MKT",
                "license_type": "oem",
                "fiscal_year": 2022,
                "depreciation_schedule": "3-year straight line",
                "last_financial_review": "2023-01-20"
            },
            {
                "asset_id": "ASSET-005",
                "cost": 75000.00,
                "cost_currency": "USD",
                "acquisition_cost": 75000.00,
                "maintenance_cost": 12000.00,
                "depreciation_value": 45000.00,
                "vendor": "Cisco Systems",
                "vendor_id": "VNDR-0015",
                "purchase_order": "PO-2020-0654",
                "cost_center": "IT-SEC-INFRA",
                "budget_code": "CAPEX-2020-IT",
                "license_type": "subscription",
                "license_count": 1,
                "license_metric": "per device",
                "fiscal_year": 2020,
                "depreciation_schedule": "5-year straight line",
                "last_financial_review": "2023-02-01"
            }
        ]
    
    def _create_sample_contracts(self):
        """Create sample contract data."""
        return [
            {
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
            },
            {
                "asset_id": "ASSET-003",
                "contract_id": "CONT-2022-0234",
                "contract_name": "Database Server Support & Maintenance",
                "expiration_date": "2026-01-09",
                "start_date": "2022-01-10",
                "renewal_type": "manual",
                "renewal_terms": "Must be renewed by written agreement 90 days prior",
                "renewal_notice_days": 90,
                "contract_value": 75000.00,
                "annual_cost": 15000.00,
                "contract_owner": "Michael Johnson",
                "vendor_contact": "enterprise-support@ibm.com",
                "contract_type": "support",
                "payment_terms": "Annual, Net 45",
                "cancellation_terms": "90 days written notice, no early termination fee",
                "document_location": "Legal Document Repository ID: DOC-6123"
            },
            {
                "asset_id": "ASSET-005",
                "contract_id": "CONT-2020-0789",
                "contract_name": "Network Security Appliance Service",
                "expiration_date": "2023-07-21",
                "start_date": "2020-07-22",
                "renewal_type": "automatic",
                "renewal_terms": "3-year renewal with 5% price increase",
                "renewal_notice_days": 120,
                "auto_renewal_date": "2023-07-22",
                "contract_value": 96000.00,
                "annual_cost": 32000.00,
                "contract_owner": "Robert Chen",
                "vendor_contact": "enterprise@cisco.com",
                "contract_type": "support and license",
                "payment_terms": "Annual, Net 30",
                "cancellation_terms": "120 days written notice, early termination fee of 25% remaining value",
                "document_location": "Legal Document Repository ID: DOC-4532"
            }
        ]
    
    def _create_sample_regulatory(self):
        """Create sample regulatory mapping data."""
        return [
            {
                "control_id": "AC-2",
                "control_framework": "NIST 800-53",
                "related_assets": ["ASSET-001", "ASSET-002", "ASSET-003", "ASSET-004"],
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
            },
            {
                "control_id": "AC-3",
                "control_framework": "NIST 800-53",
                "related_assets": ["ASSET-001", "ASSET-003", "ASSET-005"],
                "implementation_status": "partially_compliant",
                "implementation_date": "2022-08-15",
                "last_assessment_date": "2023-02-10",
                "next_assessment_date": "2023-08-10",
                "responsible_party": "Security Operations Team",
                "risk_rating": "critical",
                "evidence": [
                    {
                        "evidence_id": "EVID-AC3-001",
                        "description": "Access enforcement policy document",
                        "evidence_type": "document",
                        "collection_date": "2023-02-10",
                        "collected_by": "Robert Chen",
                        "document_location": "Compliance Repository ID: AC3-POL-V1",
                        "review_status": "needs_updates"
                    }
                ],
                "notes": "Server access enforcement is compliant, but application-level enforcement needs enhancement"
            },
            {
                "control_id": "AU-4",
                "control_framework": "NIST 800-53",
                "related_assets": ["ASSET-001", "ASSET-003", "ASSET-005"],
                "implementation_status": "compliant",
                "implementation_date": "2022-07-22",
                "last_assessment_date": "2023-01-30",
                "next_assessment_date": "2023-07-30",
                "responsible_party": "Security Operations Team",
                "risk_rating": "medium",
                "evidence": [
                    {
                        "evidence_id": "EVID-AU4-001",
                        "description": "Audit storage capacity configuration screenshots",
                        "evidence_type": "screenshot",
                        "collection_date": "2023-01-30",
                        "collected_by": "Robert Chen",
                        "document_location": "Compliance Repository ID: AU4-SCREEN-V1",
                        "review_status": "approved"
                    }
                ],
                "notes": "Adequate audit storage capacity confirmed on all critical systems"
            },
            {
                "control_id": "SC-7",
                "control_framework": "NIST 800-53",
                "related_assets": ["ASSET-005"],
                "implementation_status": "compliant",
                "implementation_date": "2020-08-15",
                "last_assessment_date": "2023-02-20",
                "next_assessment_date": "2023-08-20",
                "responsible_party": "Network Security Team",
                "risk_rating": "critical",
                "evidence": [
                    {
                        "evidence_id": "EVID-SC7-001",
                        "description": "Boundary protection architecture diagram",
                        "evidence_type": "document",
                        "collection_date": "2023-02-20",
                        "collected_by": "Mark Wilson",
                        "document_location": "Compliance Repository ID: SC7-ARCH-V3",
                        "review_status": "approved"
                    },
                    {
                        "evidence_id": "EVID-SC7-002",
                        "description": "Firewall rule configuration export",
                        "evidence_type": "configuration",
                        "collection_date": "2023-02-20",
                        "collected_by": "Mark Wilson",
                        "document_location": "Compliance Repository ID: SC7-CONFIG-V2",
                        "review_status": "approved"
                    }
                ],
                "notes": "Boundary protection is implemented through multi-layer firewall approach"
            }
        ]
    
    def _create_sample_scores(self):
        """Create sample compliance score data."""
        # Current quarter score
        current_date = date.today()
        previous_date = current_date - timedelta(days=90)
        
        return [
            {
                "score_id": f"SCORE-NIST-{current_date.year}Q1",
                "framework": "NIST 800-53",
                "score_date": str(current_date),
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
                    },
                    {
                        "metric_id": "METRIC-003",
                        "name": "Assessment Coverage",
                        "value": 90.0,
                        "weight": 0.25,
                        "weighted_score": 22.5
                    },
                    {
                        "metric_id": "METRIC-004",
                        "name": "Risk Remediation",
                        "value": 80.2,
                        "weight": 0.25,
                        "weighted_score": 20.05
                    }
                ],
                "previous_score": 84.1,
                "trend": "improving",
                "notes": "Significant improvement in control implementation rate this quarter"
            },
            {
                "score_id": f"SCORE-NIST-{previous_date.year}Q4",
                "framework": "NIST 800-53",
                "score_date": str(previous_date),
                "overall_score": 84.1,
                "metrics": [
                    {
                        "metric_id": "METRIC-001",
                        "name": "Control Implementation Rate",
                        "value": 88.2,
                        "weight": 0.3,
                        "weighted_score": 26.46
                    },
                    {
                        "metric_id": "METRIC-002",
                        "name": "Evidence Quality",
                        "value": 82.5,
                        "weight": 0.2,
                        "weighted_score": 16.5
                    },
                    {
                        "metric_id": "METRIC-003",
                        "name": "Assessment Coverage",
                        "value": 87.0,
                        "weight": 0.25,
                        "weighted_score": 21.75
                    },
                    {
                        "metric_id": "METRIC-004",
                        "name": "Risk Remediation",
                        "value": 77.6,
                        "weight": 0.25,
                        "weighted_score": 19.4
                    }
                ],
                "previous_score": 80.3,
                "trend": "improving",
                "notes": "Continued improvement across all metrics"
            },
            {
                "score_id": f"SCORE-HIPAA-{current_date.year}Q1",
                "framework": "HIPAA",
                "score_date": str(current_date),
                "overall_score": 91.7,
                "metrics": [
                    {
                        "metric_id": "METRIC-001",
                        "name": "Control Implementation Rate",
                        "value": 95.0,
                        "weight": 0.3,
                        "weighted_score": 28.5
                    },
                    {
                        "metric_id": "METRIC-002",
                        "name": "Evidence Quality",
                        "value": 90.0,
                        "weight": 0.2,
                        "weighted_score": 18.0
                    },
                    {
                        "metric_id": "METRIC-003",
                        "name": "Assessment Coverage",
                        "value": 92.0,
                        "weight": 0.25,
                        "weighted_score": 23.0
                    },
                    {
                        "metric_id": "METRIC-004",
                        "name": "Risk Remediation",
                        "value": 88.8,
                        "weight": 0.25,
                        "weighted_score": 22.2
                    }
                ],
                "previous_score": 89.5,
                "trend": "improving",
                "notes": "Strong compliance posture for HIPAA requirements"
            }
        ]
    
    def _create_sample_metrics(self):
        """Create sample scoring metrics data."""
        return [
            {
                "metric_id": "METRIC-001",
                "name": "Control Implementation Rate",
                "description": "Percentage of applicable controls that are fully implemented",
                "weight": 0.3,
                "calculation_method": "implemented_controls / applicable_controls * 100",
                "target_value": 95.0,
                "threshold_warning": 85.0,
                "threshold_critical": 75.0
            },
            {
                "metric_id": "METRIC-002",
                "name": "Evidence Quality",
                "description": "Rating of evidence quality and completeness",
                "weight": 0.2,
                "calculation_method": "sum(evidence_ratings) / count(evidence) * 100",
                "target_value": 90.0,
                "threshold_warning": 80.0,
                "threshold_critical": 70.0
            },
            {
                "metric_id": "METRIC-003",
                "name": "Assessment Coverage",
                "description": "Percentage of controls assessed within required timeframe",
                "weight": 0.25,
                "calculation_method": "assessed_controls / total_controls * 100",
                "target_value": 100.0,
                "threshold_warning": 90.0,
                "threshold_critical": 80.0
            },
            {
                "metric_id": "METRIC-004",
                "name": "Risk Remediation",
                "description": "Percentage of identified risks remediated within SLA",
                "weight": 0.25,
                "calculation_method": "remediated_risks / identified_risks * 100",
                "target_value": 90.0,
                "threshold_warning": 80.0,
                "threshold_critical": 70.0
            }
        ]
    
    def _create_sample_feedback(self):
        """Create sample user feedback data."""
        return [
            {
                "feedback_id": "FB-2023-001",
                "user_id": "user.smith",
                "feedback_date": "2023-03-15T14:22:30",
                "feedback_type": "suggestion",
                "feature": "regulatory mapping",
                "satisfaction_rating": 4,
                "usability_rating": 3,
                "feedback_text": "The evidence upload feature is useful but would benefit from batch upload capability.",
                "resolution_status": "planned",
                "resolution_notes": "Batch upload planned for Q3 2023 release"
            },
            {
                "feedback_id": "FB-2023-002",
                "user_id": "user.johnson",
                "feedback_date": "2023-03-18T09:45:12",
                "feedback_type": "issue",
                "feature": "dashboard",
                "satisfaction_rating": 2,
                "usability_rating": 2,
                "feedback_text": "The compliance score visualization is not updating in real-time when new evidence is added.",
                "resolution_status": "resolved",
                "resolution_notes": "Fixed in hotfix 2023.3.1"
            },
            {
                "feedback_id": "FB-2023-003",
                "user_id": "user.williams",
                "feedback_date": "2023-03-22T11:30:45",
                "feedback_type": "praise",
                "feature": "reporting",
                "satisfaction_rating": 5,
                "usability_rating": 5,
                "feedback_text": "The new export to PDF feature for compliance reports is excellent and saves a lot of time!",
                "resolution_status": "acknowledged",
                "resolution_notes": "Thanked user for feedback"
            },
            {
                "feedback_id": "FB-2023-004",
                "user_id": "user.chen",
                "feedback_date": "2023-03-25T16:15:33",
                "feedback_type": "suggestion",
                "feature": "integration",
                "satisfaction_rating": 3,
                "usability_rating": 4,
                "feedback_text": "Would like to see integration with our GRC tool to avoid duplicate data entry.",
                "resolution_status": "under_review",
                "resolution_notes": "Evaluating integration options with popular GRC tools"
            }
        ]
    
    def get_assets(self, asset_type=None, category=None, risk_level=None, limit=None):
        """Get assets with optional filtering."""
        filtered_assets = self.assets
        
        if asset_type:
            filtered_assets = [a for a in filtered_assets if a.get("type") == asset_type]
        
        if category:
            filtered_assets = [a for a in filtered_assets if a.get("category") == category]
        
        if risk_level:
            filtered_assets = [a for a in filtered_assets if a.get("risk_level") == risk_level]
        
        if limit and isinstance(limit, int) and limit > 0:
            filtered_assets = filtered_assets[:limit]
        
        return filtered_assets
    
    def get_asset(self, asset_id):
        """Get asset by ID."""
        for asset in self.assets:
            if asset.get("asset_id") == asset_id:
                return asset
        return None
    
    def get_financials(self, asset_id=None, vendor=None, fiscal_year=None):
        """Get financial data with optional filtering."""
        filtered_financials = self.financials
        
        if asset_id:
            filtered_financials = [f for f in filtered_financials if f.get("asset_id") == asset_id]
        
        if vendor:
            filtered_financials = [f for f in filtered_financials if f.get("vendor") == vendor]
        
        if fiscal_year and isinstance(fiscal_year, int):
            filtered_financials = [f for f in filtered_financials if f.get("fiscal_year") == fiscal_year]
        
        return filtered_financials
    
    def get_contracts(self, asset_id=None, expiring_before=None):
        """Get contract data with optional filtering."""
        filtered_contracts = self.contracts
        
        if asset_id:
            filtered_contracts = [c for c in filtered_contracts if c.get("asset_id") == asset_id]
        
        if expiring_before:
            try:
                expiry_date = date.fromisoformat(expiring_before) if isinstance(expiring_before, str) else expiring_before
                filtered_contracts = [
                    c for c in filtered_contracts if 
                    date.fromisoformat(c.get("expiration_date")) <= expiry_date
                ]
            except (ValueError, TypeError):
                # Invalid date format, ignore this filter
                pass
        
        return filtered_contracts
    
    def get_regulatory_mappings(self, control_id=None, asset_id=None, status=None):
        """Get regulatory mapping data with optional filtering."""
        filtered_mappings = self.regulatory_links
        
        if control_id:
            filtered_mappings = [m for m in filtered_mappings if m.get("control_id") == control_id]
        
        if asset_id:
            filtered_mappings = [
                m for m in filtered_mappings if 
                asset_id in m.get("related_assets", [])
            ]
        
        if status:
            filtered_mappings = [m for m in filtered_mappings if m.get("implementation_status") == status]
        
        return filtered_mappings
    
    def get_compliance_scores(self, framework=None, score_id=None):
        """Get compliance score data with optional filtering."""
        filtered_scores = self.compliance_scores
        
        if framework:
            filtered_scores = [s for s in filtered_scores if s.get("framework") == framework]
        
        if score_id:
            filtered_scores = [s for s in filtered_scores if s.get("score_id") == score_id]
        
        return filtered_scores
    
    def get_scoring_metrics(self, metric_id=None):
        """Get scoring metric data with optional filtering."""
        filtered_metrics = self.scoring_metrics
        
        if metric_id:
            filtered_metrics = [m for m in filtered_metrics if m.get("metric_id") == metric_id]
        
        return filtered_metrics
    
    def get_user_feedback(self, feedback_type=None, feature=None):
        """Get user feedback data with optional filtering."""
        filtered_feedback = self.user_feedback
        
        if feedback_type:
            filtered_feedback = [f for f in filtered_feedback if f.get("feedback_type") == feedback_type]
        
        if feature:
            filtered_feedback = [f for f in filtered_feedback if f.get("feature") == feature]
        
        return filtered_feedback
    
    def get_dashboard_summary(self):
        """Get summary statistics for the dashboard."""
        # Asset statistics
        asset_types = {}
        asset_categories = {}
        asset_risk_levels = {}
        
        for asset in self.assets:
            asset_type = asset.get("type", "unknown")
            asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
            
            category = asset.get("category", "unknown")
            asset_categories[category] = asset_categories.get(category, 0) + 1
            
            risk = asset.get("risk_level", "unknown")
            asset_risk_levels[risk] = asset_risk_levels.get(risk, 0) + 1
        
        # Financial statistics
        total_asset_value = sum(f.get("cost", 0) for f in self.financials)
        
        # Contract statistics
        contracts_expiring_soon = [
            c for c in self.contracts 
            if date.fromisoformat(c.get("expiration_date")) - date.today() <= timedelta(days=90)
        ]
        
        # Compliance statistics
        control_status = {"compliant": 0, "partially_compliant": 0, "non_compliant": 0, "not_applicable": 0}
        
        for mapping in self.regulatory_links:
            status = mapping.get("implementation_status", "unknown")
            if status in control_status:
                control_status[status] += 1
        
        # Get latest compliance scores by framework
        latest_scores = {}
        for score in self.compliance_scores:
            framework = score.get("framework")
            score_date = score.get("score_date")
            
            if not framework or not score_date:
                continue
                
            if framework not in latest_scores or score_date > latest_scores[framework].get("score_date", ""):
                latest_scores[framework] = score
        
        return {
            "assets": {
                "total_count": len(self.assets),
                "by_type": asset_types,
                "by_category": asset_categories,
                "by_risk_level": asset_risk_levels
            },
            "financials": {
                "total_asset_value": total_asset_value,
                "total_maintenance_cost": sum(f.get("maintenance_cost", 0) for f in self.financials)
            },
            "contracts": {
                "total_count": len(self.contracts),
                "expiring_within_90_days": len(contracts_expiring_soon)
            },
            "compliance": {
                "control_status": control_status,
                "latest_scores": {k: v.get("overall_score") for k, v in latest_scores.items()}
            }
        }


# Create data manager instance
dashboard_data_manager = DashboardDataManager()


# Dependency to get data manager
def get_dashboard_data_manager():
    return dashboard_data_manager


# Dashboard routes
@dashboard.get("/assets", response_model=List[AssetData], summary="Get asset data")
async def get_assets(
    asset_type: Optional[AssetType] = Query(None, description="Filter by asset type"),
    category: Optional[AssetCategory] = Query(None, description="Filter by asset category"),
    risk_level: Optional[RiskLevel] = Query(None, description="Filter by risk level"),
    limit: Optional[int] = Query(None, description="Limit number of results"),
    data_manager: DashboardDataManager = Depends(get_dashboard_data_manager)
):
    """
    Get asset data with optional filtering.
    
    Retrieve asset information from the system, optionally filtered by type,
    category, or risk level. Results can be limited to a specific number.
    """
    assets = data_manager.get_assets(
        asset_type=asset_type.value if asset_type else None,
        category=category.value if category else None,
        risk_level=risk_level.value if risk_level else None,
        limit=limit
    )
    return [AssetData(**asset) for asset in assets]


@dashboard.get("/assets/{asset_id}", response_model=AssetData, summary="Get asset by ID")
async def get_asset(
    asset_id: str,
    data_manager: DashboardDataManager = Depends(get_dashboard_data_manager)
):
    """
    Get detailed information about a specific asset.
    
    Retrieves comprehensive data about an asset identified by its unique ID.
    """
    asset = data_manager.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return AssetData(**asset)


@dashboard.get("/financials", response_model=List[FinancialData], summary="Get financial data")
async def get_financials(
    asset_id: Optional[str] = Query(None, description="Filter by asset ID"),
    vendor: Optional[str] = Query(None, description="Filter by vendor"),
    fiscal_year: Optional[int] = Query(None, description="Filter by fiscal year"),
    data_manager: DashboardDataManager = Depends(get_dashboard_data_manager)
):
    """
    Get financial data with optional filtering.
    
    Retrieve financial information from the system, optionally filtered by 
    asset ID, vendor, or fiscal year.
    """
    financials = data_manager.get_financials(
        asset_id=asset_id,
        vendor=vendor,
        fiscal_year=fiscal_year
    )
    return [FinancialData(**financial) for financial in financials]


@dashboard.get("/contracts", response_model=List[ContractData], summary="Get contract data")
async def get_contracts(
    asset_id: Optional[str] = Query(None, description="Filter by asset ID"),
    expiring_before: Optional[date] = Query(None, description="Filter by expiration date (contracts expiring before this date)"),
    data_manager: DashboardDataManager = Depends(get_dashboard_data_manager)
):
    """
    Get contract data with optional filtering.
    
    Retrieve contract information from the system, optionally filtered by
    asset ID or expiration date.
    """
    contracts = data_manager.get_contracts(
        asset_id=asset_id,
        expiring_before=expiring_before
    )
    return [ContractData(**contract) for contract in contracts]


@dashboard.get("/regulatory", response_model=List[RegulatoryMapping], summary="Get regulatory mapping data")
async def get_regulatory_links(
    control_id: Optional[str] = Query(None, description="Filter by control ID"),
    asset_id: Optional[str] = Query(None, description="Filter by asset ID"),
    status: Optional[ComplianceStatus] = Query(None, description="Filter by implementation status"),
    data_manager: DashboardDataManager = Depends(get_dashboard_data_manager)
):
    """
    Get regulatory mapping data with optional filtering.
    
    Retrieve regulatory mapping information from the system, optionally filtered
    by control ID, asset ID, or implementation status.
    """
    mappings = data_manager.get_regulatory_mappings(
        control_id=control_id,
        asset_id=asset_id,
        status=status.value if status else None
    )
    return [RegulatoryMapping(**mapping) for mapping in mappings]


@dashboard.get("/scores", response_model=List[ComplianceScore], summary="Get compliance score data")
async def get_compliance_scores(
    framework: Optional[str] = Query(None, description="Filter by framework"),
    score_id: Optional[str] = Query(None, description="Filter by score ID"),
    data_manager: DashboardDataManager = Depends(get_dashboard_data_manager)
):
    """
    Get compliance score data with optional filtering.
    
    Retrieve compliance score information from the system, optionally filtered
    by framework or score ID.
    """
    scores = data_manager.get_compliance_scores(
        framework=framework,
        score_id=score_id
    )
    return [ComplianceScore(**score) for score in scores]


@dashboard.get("/metrics", response_model=List[ScoringMetric], summary="Get scoring metric data")
async def get_scoring_metrics(
    metric_id: Optional[str] = Query(None, description="Filter by metric ID"),
    data_manager: DashboardDataManager = Depends(get_dashboard_data_manager)
):
    """
    Get scoring metric data with optional filtering.
    
    Retrieve scoring metric information from the system, optionally filtered
    by metric ID.
    """
    metrics = data_manager.get_scoring_metrics(
        metric_id=metric_id
    )
    return [ScoringMetric(**metric) for metric in metrics]


@dashboard.get("/feedback", response_model=List[UserFeedback], summary="Get user feedback data")
async def get_user_feedback(
    feedback_type: Optional[str] = Query(None, description="Filter by feedback type"),
    feature: Optional[str] = Query(None, description="Filter by feature"),
    data_manager: DashboardDataManager = Depends(get_dashboard_data_manager)
):
    """
    Get user feedback data with optional filtering.
    
    Retrieve user feedback information from the system, optionally filtered
    by feedback type or feature.
    """
    feedback = data_manager.get_user_feedback(
        feedback_type=feedback_type,
        feature=feature
    )
    return [UserFeedback(**f) for f in feedback]


@dashboard.get("/summary", summary="Get dashboard summary statistics")
async def get_dashboard_summary(
    data_manager: DashboardDataManager = Depends(get_dashboard_data_manager)
):
    """
    Get summary statistics for the dashboard.
    
    Retrieves aggregated statistics about assets, financials, contracts, and
    compliance status for display on the dashboard.
    """
    return data_manager.get_dashboard_summary()