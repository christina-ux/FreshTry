"""
Scoring API endpoints for PolicyEdgeAI.

Provides compliance scoring capabilities based on control implementation,
asset coverage, evidence quality, and risk remediation.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any, Optional
import logging
from datetime import date, datetime, timedelta
import json
import os
import math
import random
from models.taxonomy import (
    ComplianceScore, ScoringMetric, AssetData, RegulatoryMapping,
    ComplianceStatus, RiskLevel
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create router
scoring = APIRouter(
    prefix="/api/scoring",
    tags=["scoring"],
    responses={404: {"description": "Scoring data not found"}}
)


class ScoringEngine:
    """Scoring engine for compliance assessment."""
    
    def __init__(self):
        """Initialize the scoring engine."""
        self.data_dir = os.path.join(os.getcwd(), "data", "scoring")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load or create scoring configuration
        self.config = self._load_or_create_config()
        
        # Load or create historical scores
        self.historical_scores = self._load_or_create_historical()
    
    def _load_or_create_config(self):
        """Load scoring configuration or create default if not exists."""
        config_path = os.path.join(self.data_dir, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading scoring configuration: {str(e)}")
                return self._create_default_config()
        else:
            config = self._create_default_config()
            try:
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving scoring configuration: {str(e)}")
            return config
    
    def _create_default_config(self):
        """Create default scoring configuration."""
        return {
            "metrics": [
                {
                    "id": "control_implementation",
                    "name": "Control Implementation Rate",
                    "description": "Percentage of applicable controls that are fully implemented",
                    "weight": 0.35,
                    "calculation": "implemented_controls / applicable_controls * 100",
                    "target": 95.0,
                    "warning_threshold": 85.0,
                    "critical_threshold": 75.0
                },
                {
                    "id": "asset_coverage",
                    "name": "Asset Coverage",
                    "description": "Percentage of assets with mapped controls",
                    "weight": 0.25,
                    "calculation": "assets_with_controls / total_assets * 100",
                    "target": 90.0,
                    "warning_threshold": 80.0,
                    "critical_threshold": 70.0
                },
                {
                    "id": "evidence_quality",
                    "name": "Evidence Quality",
                    "description": "Quality rating of evidence provided for controls",
                    "weight": 0.20,
                    "calculation": "sum(evidence_ratings) / count(evidence) * 100",
                    "target": 90.0,
                    "warning_threshold": 80.0,
                    "critical_threshold": 70.0
                },
                {
                    "id": "risk_remediation",
                    "name": "Risk Remediation",
                    "description": "Percentage of identified risks that have been remediated",
                    "weight": 0.20,
                    "calculation": "remediated_risks / identified_risks * 100",
                    "target": 90.0,
                    "warning_threshold": 80.0,
                    "critical_threshold": 70.0
                }
            ],
            "frameworks": [
                {
                    "id": "NIST_800_53",
                    "name": "NIST 800-53",
                    "version": "Rev 5",
                    "weights": {
                        "control_implementation": 0.35,
                        "asset_coverage": 0.25,
                        "evidence_quality": 0.20,
                        "risk_remediation": 0.20
                    }
                },
                {
                    "id": "HIPAA",
                    "name": "HIPAA",
                    "version": "2013",
                    "weights": {
                        "control_implementation": 0.40,
                        "asset_coverage": 0.20,
                        "evidence_quality": 0.25,
                        "risk_remediation": 0.15
                    }
                },
                {
                    "id": "PCI_DSS",
                    "name": "PCI DSS",
                    "version": "4.0",
                    "weights": {
                        "control_implementation": 0.30,
                        "asset_coverage": 0.30,
                        "evidence_quality": 0.20,
                        "risk_remediation": 0.20
                    }
                }
            ],
            "score_thresholds": {
                "excellent": 90.0,
                "good": 80.0,
                "satisfactory": 70.0,
                "needs_improvement": 60.0,
                "poor": 0.0
            },
            "asset_types": {
                "server": 1.2,
                "endpoint": 1.0,
                "network_device": 1.3,
                "mobile_device": 0.8,
                "cloud_service": 1.1,
                "application": 1.0,
                "database": 1.2,
                "iot_device": 0.7
            },
            "control_families": {
                "access_control": 1.3,
                "audit_and_accountability": 1.1,
                "security_assessment": 1.0,
                "configuration_management": 1.2,
                "identification_and_authentication": 1.3,
                "incident_response": 1.1,
                "risk_assessment": 1.0,
                "system_and_communications_protection": 1.2,
                "system_and_information_integrity": 1.1
            }
        }
    
    def _load_or_create_historical(self):
        """Load historical score data or create default if not exists."""
        historical_path = os.path.join(self.data_dir, "historical_scores.json")
        if os.path.exists(historical_path):
            try:
                with open(historical_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading historical scores: {str(e)}")
                return self._create_default_historical()
        else:
            historical = self._create_default_historical()
            try:
                with open(historical_path, 'w') as f:
                    json.dump(historical, f, indent=2, default=str)
            except Exception as e:
                logger.error(f"Error saving historical scores: {str(e)}")
            return historical
    
    def _create_default_historical(self):
        """Create default historical score data."""
        today = date.today()
        historical = {"frameworks": {}}
        
        for framework in self.config["frameworks"]:
            framework_id = framework["id"]
            historical["frameworks"][framework_id] = []
            
            # Create historical data for the past 12 months
            for i in range(12, 0, -1):
                score_date = today.replace(day=1) - timedelta(days=i * 30)
                
                # Create a score with a slight upward trend
                base_score = 70.0 + (i / 12.0) * 15.0  # Start at 70%, trend up to 85%
                # Add some randomness
                random_factor = random.uniform(-3.0, 3.0)
                overall_score = min(max(base_score + random_factor, 60.0), 95.0)
                
                # Create metric scores with some variation
                metrics = [
                    {
                        "id": "control_implementation",
                        "name": "Control Implementation Rate",
                        "value": min(max(overall_score + random.uniform(-5.0, 5.0), 60.0), 98.0),
                        "weight": framework["weights"]["control_implementation"],
                        "weighted_score": 0  # Will be calculated later
                    },
                    {
                        "id": "asset_coverage",
                        "name": "Asset Coverage",
                        "value": min(max(overall_score + random.uniform(-7.0, 3.0), 55.0), 97.0),
                        "weight": framework["weights"]["asset_coverage"],
                        "weighted_score": 0  # Will be calculated later
                    },
                    {
                        "id": "evidence_quality",
                        "name": "Evidence Quality",
                        "value": min(max(overall_score + random.uniform(-4.0, 4.0), 65.0), 96.0),
                        "weight": framework["weights"]["evidence_quality"],
                        "weighted_score": 0  # Will be calculated later
                    },
                    {
                        "id": "risk_remediation",
                        "name": "Risk Remediation",
                        "value": min(max(overall_score + random.uniform(-6.0, 2.0), 58.0), 95.0),
                        "weight": framework["weights"]["risk_remediation"],
                        "weighted_score": 0  # Will be calculated later
                    }
                ]
                
                # Calculate weighted scores and recalculate overall score
                overall_score = 0
                for metric in metrics:
                    metric["weighted_score"] = metric["value"] * metric["weight"]
                    overall_score += metric["weighted_score"]
                
                # Determine trend
                trend = "stable"
                if i > 1:
                    prev_score = historical["frameworks"][framework_id][-1]["overall_score"] if historical["frameworks"][framework_id] else 0
                    if overall_score > prev_score + 1.0:
                        trend = "improving"
                    elif overall_score < prev_score - 1.0:
                        trend = "declining"
                
                historical["frameworks"][framework_id].append({
                    "score_id": f"{framework_id}-{score_date.strftime('%Y%m')}",
                    "framework": framework["name"],
                    "score_date": score_date.isoformat(),
                    "overall_score": round(overall_score, 1),
                    "metrics": metrics,
                    "trend": trend,
                    "notes": f"Historical score for {framework['name']} - {score_date.strftime('%B %Y')}"
                })
        
        return historical
    
    def get_framework_config(self, framework_id):
        """Get configuration for a specific framework."""
        for framework in self.config["frameworks"]:
            if framework["id"] == framework_id:
                return framework
        return None
    
    def get_metric_config(self, metric_id):
        """Get configuration for a specific metric."""
        for metric in self.config["metrics"]:
            if metric["id"] == metric_id:
                return metric
        return None
    
    def get_historical_scores(self, framework_id=None, limit=None):
        """Get historical scores for a framework."""
        if framework_id:
            scores = self.historical_scores["frameworks"].get(framework_id, [])
        else:
            # Flatten all framework scores
            scores = []
            for framework_scores in self.historical_scores["frameworks"].values():
                scores.extend(framework_scores)
            
            # Sort by date (newest first)
            scores.sort(key=lambda s: s["score_date"], reverse=True)
        
        if limit and isinstance(limit, int) and limit > 0:
            return scores[:limit]
        
        return scores
    
    def calculate_score(self, framework_id, control_data, asset_data, mapping_data, evidence_data=None):
        """
        Calculate compliance score for a framework.
        
        Args:
            framework_id (str): Framework identifier
            control_data (list): List of controls
            asset_data (list): List of assets
            mapping_data (list): List of mappings between controls and assets
            evidence_data (list, optional): List of evidence items
            
        Returns:
            dict: Calculated score
        """
        # Get framework configuration
        framework = self.get_framework_config(framework_id)
        if not framework:
            raise ValueError(f"Framework {framework_id} not found")
        
        # Initialize result
        result = {
            "score_id": f"{framework_id}-{date.today().strftime('%Y%m%d')}",
            "framework": framework["name"],
            "score_date": date.today().isoformat(),
            "metrics": [],
            "previous_score": None,
            "trend": "stable"
        }
        
        # Initialize metrics
        metrics_result = {}
        
        # Calculate Control Implementation Rate
        if control_data:
            # Count controls by status
            total_controls = len(control_data)
            implemented_controls = sum(1 for c in control_data if c.get("implementation_status") == "compliant")
            partially_implemented = sum(1 for c in control_data if c.get("implementation_status") == "partially_compliant")
            non_implemented = sum(1 for c in control_data if c.get("implementation_status") == "non_compliant")
            not_applicable = sum(1 for c in control_data if c.get("implementation_status") == "not_applicable")
            
            # Calculate applicable controls
            applicable_controls = total_controls - not_applicable
            
            # Calculate implementation rate (count partially implemented as 0.5)
            if applicable_controls > 0:
                implementation_rate = (implemented_controls + (partially_implemented * 0.5)) / applicable_controls * 100
            else:
                implementation_rate = 0
            
            metrics_result["control_implementation"] = {
                "id": "control_implementation",
                "name": "Control Implementation Rate",
                "value": round(implementation_rate, 1),
                "weight": framework["weights"]["control_implementation"],
                "details": {
                    "total_controls": total_controls,
                    "applicable_controls": applicable_controls,
                    "implemented_controls": implemented_controls,
                    "partially_implemented": partially_implemented,
                    "non_implemented": non_implemented,
                    "not_applicable": not_applicable
                }
            }
        else:
            # No control data available
            metrics_result["control_implementation"] = {
                "id": "control_implementation",
                "name": "Control Implementation Rate",
                "value": 0.0,
                "weight": framework["weights"]["control_implementation"],
                "details": {
                    "total_controls": 0,
                    "applicable_controls": 0,
                    "implemented_controls": 0,
                    "partially_implemented": 0,
                    "non_implemented": 0,
                    "not_applicable": 0
                }
            }
        
        # Calculate Asset Coverage
        if asset_data and mapping_data:
            total_assets = len(asset_data)
            
            # Get assets with controls
            assets_with_controls = set()
            for mapping in mapping_data:
                assets_with_controls.update(mapping.get("related_assets", []))
            
            # Calculate coverage
            assets_with_controls_count = len(assets_with_controls)
            if total_assets > 0:
                asset_coverage = assets_with_controls_count / total_assets * 100
            else:
                asset_coverage = 0
            
            metrics_result["asset_coverage"] = {
                "id": "asset_coverage",
                "name": "Asset Coverage",
                "value": round(asset_coverage, 1),
                "weight": framework["weights"]["asset_coverage"],
                "details": {
                    "total_assets": total_assets,
                    "assets_with_controls": assets_with_controls_count,
                    "assets_without_controls": total_assets - assets_with_controls_count
                }
            }
        else:
            # No asset or mapping data available
            metrics_result["asset_coverage"] = {
                "id": "asset_coverage",
                "name": "Asset Coverage",
                "value": 0.0,
                "weight": framework["weights"]["asset_coverage"],
                "details": {
                    "total_assets": 0,
                    "assets_with_controls": 0,
                    "assets_without_controls": 0
                }
            }
        
        # Calculate Evidence Quality
        if evidence_data:
            total_evidence = len(evidence_data)
            evidence_ratings = [
                self._calculate_evidence_quality(e) for e in evidence_data
            ]
            
            if total_evidence > 0:
                average_rating = sum(evidence_ratings) / total_evidence
                evidence_quality = average_rating * 100  # Convert to percentage
            else:
                evidence_quality = 0
            
            metrics_result["evidence_quality"] = {
                "id": "evidence_quality",
                "name": "Evidence Quality",
                "value": round(evidence_quality, 1),
                "weight": framework["weights"]["evidence_quality"],
                "details": {
                    "total_evidence": total_evidence,
                    "average_rating": round(average_rating, 2) if total_evidence > 0 else 0
                }
            }
        else:
            # Use a simpler method if no evidence data is provided
            # Base evidence quality on control implementation rate with a slight reduction
            if "control_implementation" in metrics_result:
                evidence_quality = max(0, metrics_result["control_implementation"]["value"] - 10)
            else:
                evidence_quality = 0
            
            metrics_result["evidence_quality"] = {
                "id": "evidence_quality",
                "name": "Evidence Quality",
                "value": round(evidence_quality, 1),
                "weight": framework["weights"]["evidence_quality"],
                "details": {
                    "total_evidence": 0,
                    "estimated_based_on": "control implementation rate",
                    "adjustment_factor": -10
                }
            }
        
        # Calculate Risk Remediation
        # For simplicity, estimate based on control implementation if no specific data provided
        if "control_implementation" in metrics_result:
            risk_remediation = metrics_result["control_implementation"]["value"] * 0.9  # Slight reduction
            
            metrics_result["risk_remediation"] = {
                "id": "risk_remediation",
                "name": "Risk Remediation",
                "value": round(risk_remediation, 1),
                "weight": framework["weights"]["risk_remediation"],
                "details": {
                    "estimated_based_on": "control implementation rate",
                    "adjustment_factor": 0.9
                }
            }
        else:
            metrics_result["risk_remediation"] = {
                "id": "risk_remediation",
                "name": "Risk Remediation",
                "value": 0.0,
                "weight": framework["weights"]["risk_remediation"],
                "details": {
                    "estimated_based_on": "no data available"
                }
            }
        
        # Calculate weighted scores and overall score
        overall_score = 0
        for metric_id, metric in metrics_result.items():
            metric["weighted_score"] = metric["value"] * metric["weight"]
            overall_score += metric["weighted_score"]
        
        # Add metrics to result
        result["metrics"] = list(metrics_result.values())
        result["overall_score"] = round(overall_score, 1)
        
        # Determine rating based on thresholds
        for rating, threshold in sorted(self.config["score_thresholds"].items(), key=lambda x: x[1], reverse=True):
            if overall_score >= threshold:
                result["rating"] = rating
                break
        
        # Get previous score for trend
        historical_scores = self.get_historical_scores(framework_id)
        if historical_scores:
            previous_score = historical_scores[0]["overall_score"]
            result["previous_score"] = previous_score
            
            # Determine trend
            if overall_score > previous_score + 1.0:
                result["trend"] = "improving"
            elif overall_score < previous_score - 1.0:
                result["trend"] = "declining"
        
        return result
    
    def _calculate_evidence_quality(self, evidence):
        """
        Calculate evidence quality rating (0.0 to 1.0).
        
        This is a simplified example. In a real implementation, this would evaluate
        factors like completeness, relevance, timeliness, etc.
        """
        # Start with base rating
        rating = 0.7
        
        # Adjust based on review status
        review_status = evidence.get("review_status", "").lower()
        if review_status == "approved":
            rating += 0.2
        elif review_status == "needs_updates":
            rating -= 0.1
        
        # Adjust based on evidence type
        evidence_type = evidence.get("evidence_type", "").lower()
        if evidence_type == "document":
            rating += 0.05
        elif evidence_type == "screenshot":
            rating += 0.0
        elif evidence_type == "configuration":
            rating += 0.1
        
        # Ensure rating is within bounds
        return max(0.0, min(1.0, rating))
    
    def save_score(self, score):
        """
        Save a calculated score to historical data.
        
        Args:
            score (dict): Calculated score data
            
        Returns:
            bool: Success status
        """
        try:
            framework_id = score["score_id"].split("-")[0]
            
            # Add to historical data
            if framework_id not in self.historical_scores["frameworks"]:
                self.historical_scores["frameworks"][framework_id] = []
            
            # Insert at beginning (newest first)
            self.historical_scores["frameworks"][framework_id].insert(0, score)
            
            # Save to file
            historical_path = os.path.join(self.data_dir, "historical_scores.json")
            with open(historical_path, 'w') as f:
                json.dump(self.historical_scores, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving score: {str(e)}")
            return False


# Create scoring engine instance
scoring_engine = ScoringEngine()


# Dependency to get scoring engine
def get_scoring_engine():
    return scoring_engine


# Scoring endpoints
@scoring.get("/score", summary="Get compliance score for a framework")
async def get_compliance_score(
    framework_id: str = Query(..., description="Framework identifier (e.g., NIST_800_53, HIPAA, PCI_DSS)"),
    engine: ScoringEngine = Depends(get_scoring_engine)
):
    """
    Calculate compliance score for a framework.
    
    This endpoint calculates a compliance score based on control implementation,
    asset coverage, evidence quality, and risk remediation metrics.
    """
    try:
        # Check if framework is configured
        framework = engine.get_framework_config(framework_id)
        if not framework:
            raise HTTPException(status_code=404, detail=f"Framework {framework_id} not found")
        
        # Mock data for demonstration - in a real implementation, this would fetch actual data
        control_data = [
            {"id": "AC-1", "implementation_status": "compliant"},
            {"id": "AC-2", "implementation_status": "compliant"},
            {"id": "AC-3", "implementation_status": "partially_compliant"},
            {"id": "AC-4", "implementation_status": "non_compliant"},
            {"id": "AC-5", "implementation_status": "compliant"},
            {"id": "AC-6", "implementation_status": "partially_compliant"},
            {"id": "AC-7", "implementation_status": "compliant"},
            {"id": "AC-8", "implementation_status": "compliant"},
            {"id": "AU-1", "implementation_status": "compliant"},
            {"id": "AU-2", "implementation_status": "partially_compliant"},
            {"id": "AU-3", "implementation_status": "compliant"},
            {"id": "AU-4", "implementation_status": "compliant"},
            {"id": "AU-5", "implementation_status": "compliant"},
            {"id": "IA-1", "implementation_status": "non_compliant"},
            {"id": "IA-2", "implementation_status": "partially_compliant"},
            {"id": "IA-3", "implementation_status": "compliant"},
            {"id": "IA-4", "implementation_status": "compliant"},
            {"id": "SC-1", "implementation_status": "compliant"},
            {"id": "SC-2", "implementation_status": "partially_compliant"},
            {"id": "SC-3", "implementation_status": "non_compliant"},
            {"id": "SC-4", "implementation_status": "not_applicable"},
            {"id": "SC-5", "implementation_status": "compliant"},
        ]
        
        asset_data = [
            {"asset_id": "ASSET-001", "type": "server"},
            {"asset_id": "ASSET-002", "type": "endpoint"},
            {"asset_id": "ASSET-003", "type": "server"},
            {"asset_id": "ASSET-004", "type": "endpoint"},
            {"asset_id": "ASSET-005", "type": "network_device"},
        ]
        
        mapping_data = [
            {"control_id": "AC-1", "related_assets": ["ASSET-001", "ASSET-002", "ASSET-003", "ASSET-004", "ASSET-005"]},
            {"control_id": "AC-2", "related_assets": ["ASSET-001", "ASSET-003"]},
            {"control_id": "AC-3", "related_assets": ["ASSET-001", "ASSET-003", "ASSET-005"]},
            {"control_id": "AC-5", "related_assets": ["ASSET-001", "ASSET-003"]},
            {"control_id": "AC-6", "related_assets": ["ASSET-001", "ASSET-002", "ASSET-003", "ASSET-004"]},
            {"control_id": "AC-7", "related_assets": ["ASSET-001", "ASSET-003"]},
            {"control_id": "AU-1", "related_assets": ["ASSET-001", "ASSET-003"]},
            {"control_id": "AU-2", "related_assets": ["ASSET-001", "ASSET-003"]},
            {"control_id": "AU-3", "related_assets": ["ASSET-001", "ASSET-003"]},
            {"control_id": "AU-4", "related_assets": ["ASSET-001", "ASSET-003"]},
            {"control_id": "AU-5", "related_assets": ["ASSET-001", "ASSET-003"]},
            {"control_id": "IA-2", "related_assets": ["ASSET-001", "ASSET-002", "ASSET-003", "ASSET-004"]},
            {"control_id": "IA-3", "related_assets": ["ASSET-005"]},
            {"control_id": "IA-4", "related_assets": ["ASSET-001", "ASSET-002", "ASSET-003", "ASSET-004"]},
            {"control_id": "SC-1", "related_assets": ["ASSET-001", "ASSET-003", "ASSET-005"]},
            {"control_id": "SC-2", "related_assets": ["ASSET-001", "ASSET-003"]},
            {"control_id": "SC-5", "related_assets": ["ASSET-005"]},
        ]
        
        evidence_data = [
            {
                "control_id": "AC-1",
                "evidence_type": "document",
                "review_status": "approved"
            },
            {
                "control_id": "AC-2",
                "evidence_type": "configuration",
                "review_status": "approved"
            },
            {
                "control_id": "AC-3",
                "evidence_type": "screenshot",
                "review_status": "needs_updates"
            },
            {
                "control_id": "AU-1",
                "evidence_type": "document",
                "review_status": "approved"
            },
            {
                "control_id": "IA-2",
                "evidence_type": "configuration",
                "review_status": "approved"
            },
            {
                "control_id": "SC-1",
                "evidence_type": "document",
                "review_status": "approved"
            },
        ]
        
        # Calculate score
        score = engine.calculate_score(framework_id, control_data, asset_data, mapping_data, evidence_data)
        
        # Save score to historical data
        engine.save_score(score)
        
        return score
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating compliance score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@scoring.get("/history", summary="Get historical compliance scores")
async def get_historical_scores(
    framework_id: Optional[str] = Query(None, description="Framework identifier (optional)"),
    limit: Optional[int] = Query(12, description="Maximum number of scores to return"),
    engine: ScoringEngine = Depends(get_scoring_engine)
):
    """
    Get historical compliance scores.
    
    This endpoint retrieves historical compliance scores for trend analysis,
    optionally filtered by framework.
    """
    try:
        scores = engine.get_historical_scores(framework_id, limit)
        return {"scores": scores}
        
    except Exception as e:
        logger.error(f"Error retrieving historical scores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@scoring.get("/metrics", summary="Get scoring metrics configuration")
async def get_scoring_metrics(
    engine: ScoringEngine = Depends(get_scoring_engine)
):
    """
    Get scoring metrics configuration.
    
    This endpoint retrieves the configuration for scoring metrics,
    including weights, targets, and thresholds.
    """
    try:
        return {"metrics": engine.config["metrics"]}
        
    except Exception as e:
        logger.error(f"Error retrieving scoring metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@scoring.get("/frameworks", summary="Get configured frameworks")
async def get_frameworks(
    engine: ScoringEngine = Depends(get_scoring_engine)
):
    """
    Get configured frameworks.
    
    This endpoint retrieves the list of configured frameworks
    for compliance scoring.
    """
    try:
        return {"frameworks": engine.config["frameworks"]}
        
    except Exception as e:
        logger.error(f"Error retrieving frameworks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@scoring.get("/dashboard", summary="Get scoring dashboard data")
async def get_scoring_dashboard(
    engine: ScoringEngine = Depends(get_scoring_engine)
):
    """
    Get scoring dashboard data.
    
    This endpoint retrieves summary data for the scoring dashboard,
    including latest scores, trends, and comparison metrics.
    """
    try:
        # Get latest score for each framework
        latest_scores = {}
        for framework_id in engine.historical_scores["frameworks"]:
            scores = engine.get_historical_scores(framework_id, 1)
            if scores:
                latest_scores[framework_id] = scores[0]
        
        # Get historical trends (last 6 months)
        trends = {}
        for framework_id in engine.historical_scores["frameworks"]:
            scores = engine.get_historical_scores(framework_id, 6)
            trends[framework_id] = [
                {"date": score["score_date"], "score": score["overall_score"]}
                for score in scores
            ]
        
        # Calculate average improvement
        improvements = {}
        for framework_id, trend_data in trends.items():
            if len(trend_data) >= 2:
                oldest = trend_data[-1]["score"]
                newest = trend_data[0]["score"]
                improvements[framework_id] = newest - oldest
        
        # Generate summary
        return {
            "latest_scores": latest_scores,
            "trends": trends,
            "improvements": improvements,
            "thresholds": engine.config["score_thresholds"]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving scoring dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@scoring.get("/report/{framework_id}", summary="Get detailed compliance score report")
async def get_compliance_report(
    framework_id: str,
    engine: ScoringEngine = Depends(get_scoring_engine)
):
    """
    Get detailed compliance score report for a framework.
    
    This endpoint generates a comprehensive report on compliance status,
    including control implementation details, asset coverage, and recommendations.
    """
    try:
        # Check if framework is configured
        framework = engine.get_framework_config(framework_id)
        if not framework:
            raise HTTPException(status_code=404, detail=f"Framework {framework_id} not found")
        
        # Get latest score
        scores = engine.get_historical_scores(framework_id, 1)
        if not scores:
            raise HTTPException(status_code=404, detail=f"No scores found for framework {framework_id}")
        
        latest_score = scores[0]
        
        # Get historical trend
        historical = engine.get_historical_scores(framework_id, 6)
        trend_data = [
            {"date": score["score_date"], "score": score["overall_score"]}
            for score in historical
        ]
        
        # Generate recommendations based on metric values
        recommendations = []
        for metric in latest_score["metrics"]:
            metric_config = engine.get_metric_config(metric["id"])
            if not metric_config:
                continue
                
            if metric["value"] < metric_config["critical_threshold"]:
                recommendations.append({
                    "priority": "high",
                    "metric": metric["name"],
                    "recommendation": f"Critical: Immediate attention needed for {metric['name']}. Current value of {metric['value']}% is below the critical threshold of {metric_config['critical_threshold']}%."
                })
            elif metric["value"] < metric_config["warning_threshold"]:
                recommendations.append({
                    "priority": "medium",
                    "metric": metric["name"],
                    "recommendation": f"Warning: Improvement needed for {metric['name']}. Current value of {metric['value']}% is below the warning threshold of {metric_config['warning_threshold']}%."
                })
            elif metric["value"] < metric_config["target"]:
                recommendations.append({
                    "priority": "low",
                    "metric": metric["name"],
                    "recommendation": f"Consider improving {metric['name']} to reach target of {metric_config['target']}%. Current value is {metric['value']}%."
                })
        
        # Summarize control implementation details
        control_implementation = next((m for m in latest_score["metrics"] if m["id"] == "control_implementation"), None)
        implementation_details = control_implementation["details"] if control_implementation else {}
        
        # Generate report
        report = {
            "framework": framework["name"],
            "score_date": latest_score["score_date"],
            "overall_score": latest_score["overall_score"],
            "rating": latest_score.get("rating", "unknown"),
            "trend": latest_score.get("trend", "stable"),
            "metrics": latest_score["metrics"],
            "historical_trend": trend_data,
            "implementation_details": implementation_details,
            "recommendations": recommendations,
            "summary": f"The overall compliance score for {framework['name']} is {latest_score['overall_score']}%, which is rated as '{latest_score.get('rating', 'unknown')}'. The compliance posture is {latest_score.get('trend', 'stable')}."
        }
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))