"""
Data aggregator for intelligence features.

Collects and processes data from various PolicyEdge sources to create
intelligence feeds and memos.
"""

import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import json
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregates data from various PolicyEdge sources for intelligence analysis."""
    
    def __init__(self):
        """Initialize the data aggregator."""
        self.data_dir = os.path.join(os.getcwd(), "data", "intelligence")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data cache
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # 5 minutes
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[key]
    
    def _cache_data(self, key: str, data: Any) -> None:
        """Cache data with expiry time."""
        self.cache[key] = data
        self.cache_expiry[key] = datetime.now() + timedelta(seconds=self.cache_duration)
    
    def get_compliance_changes(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Get compliance score changes in the specified time window.
        
        Args:
            hours_back (int): Number of hours to look back for changes
            
        Returns:
            List[Dict[str, Any]]: List of compliance changes
        """
        cache_key = f"compliance_changes_{hours_back}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # In a real implementation, this would query actual compliance data
            # For now, we'll simulate recent changes
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Simulate compliance changes
            changes = [
                {
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "framework": "NIST 800-53",
                    "change_type": "score_improvement",
                    "old_score": 84.1,
                    "new_score": 87.3,
                    "change": 3.2,
                    "details": {
                        "improved_metrics": ["Control Implementation Rate", "Evidence Quality"],
                        "reason": "Implementation of AC-2 and AU-4 controls"
                    }
                },
                {
                    "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
                    "framework": "HIPAA",
                    "change_type": "control_implementation",
                    "control_id": "164.308(a)(5)(ii)(C)",
                    "old_status": "partially_compliant",
                    "new_status": "compliant",
                    "details": {
                        "control_name": "Assigned Security Responsibility",
                        "evidence_added": "Security policy document updated"
                    }
                },
                {
                    "timestamp": (datetime.now() - timedelta(hours=12)).isoformat(),
                    "framework": "PCI DSS",
                    "change_type": "risk_level_change",
                    "control_id": "3.2.1",
                    "old_risk": "high",
                    "new_risk": "medium",
                    "details": {
                        "control_name": "Do not store sensitive authentication data",
                        "reason": "Enhanced encryption implementation"
                    }
                }
            ]
            
            # Filter changes within time window
            filtered_changes = [
                change for change in changes
                if datetime.fromisoformat(change["timestamp"]) >= cutoff_time
            ]
            
            self._cache_data(cache_key, filtered_changes)
            return filtered_changes
            
        except Exception as e:
            logger.error(f"Error getting compliance changes: {str(e)}")
            return []
    
    def get_asset_changes(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Get asset changes in the specified time window.
        
        Args:
            hours_back (int): Number of hours to look back for changes
            
        Returns:
            List[Dict[str, Any]]: List of asset changes
        """
        cache_key = f"asset_changes_{hours_back}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Simulate asset changes
            changes = [
                {
                    "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                    "change_type": "new_asset",
                    "asset_id": "ASSET-006",
                    "asset_name": "Database Backup Server",
                    "asset_type": "server",
                    "risk_level": "medium",
                    "details": {
                        "department": "IT Operations",
                        "location": "Secondary Data Center",
                        "data_classification": "internal"
                    }
                },
                {
                    "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                    "change_type": "risk_level_change",
                    "asset_id": "ASSET-003",
                    "asset_name": "Customer Database Server",
                    "old_risk": "critical",
                    "new_risk": "high",
                    "details": {
                        "reason": "Security patches applied",
                        "updated_controls": ["AC-3", "SC-7"]
                    }
                },
                {
                    "timestamp": (datetime.now() - timedelta(hours=8)).isoformat(),
                    "change_type": "status_change",
                    "asset_id": "ASSET-002",
                    "asset_name": "Finance Department Workstation",
                    "old_status": "active",
                    "new_status": "maintenance",
                    "details": {
                        "reason": "Scheduled security updates",
                        "estimated_completion": (datetime.now() + timedelta(hours=2)).isoformat()
                    }
                }
            ]
            
            # Filter changes within time window
            filtered_changes = [
                change for change in changes
                if datetime.fromisoformat(change["timestamp"]) >= cutoff_time
            ]
            
            self._cache_data(cache_key, filtered_changes)
            return filtered_changes
            
        except Exception as e:
            logger.error(f"Error getting asset changes: {str(e)}")
            return []
    
    def get_contract_alerts(self, days_ahead: int = 90) -> List[Dict[str, Any]]:
        """
        Get contract expiration alerts.
        
        Args:
            days_ahead (int): Number of days ahead to check for expirations
            
        Returns:
            List[Dict[str, Any]]: List of contract alerts
        """
        cache_key = f"contract_alerts_{days_ahead}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            alert_date = date.today() + timedelta(days=days_ahead)
            
            # Simulate contract expiration alerts
            alerts = [
                {
                    "contract_id": "CONT-2020-0789",
                    "contract_name": "Network Security Appliance Service",
                    "asset_id": "ASSET-005",
                    "asset_name": "Network Firewall",
                    "expiration_date": "2023-07-21",
                    "days_until_expiration": 45,
                    "annual_cost": 32000.00,
                    "renewal_type": "automatic",
                    "vendor": "Cisco Systems",
                    "urgency": "high",
                    "details": {
                        "renewal_notice_days": 120,
                        "auto_renewal_date": "2023-07-22",
                        "contract_owner": "Robert Chen"
                    }
                },
                {
                    "contract_id": "CONT-2022-0234",
                    "contract_name": "Database Server Support & Maintenance",
                    "asset_id": "ASSET-003",
                    "asset_name": "Customer Database Server",
                    "expiration_date": "2026-01-09",
                    "days_until_expiration": 85,
                    "annual_cost": 15000.00,
                    "renewal_type": "manual",
                    "vendor": "IBM",
                    "urgency": "medium",
                    "details": {
                        "renewal_notice_days": 90,
                        "contract_owner": "Michael Johnson"
                    }
                }
            ]
            
            # Filter alerts for contracts expiring within the specified window
            today = date.today()
            filtered_alerts = []
            
            for alert in alerts:
                exp_date = date.fromisoformat(alert["expiration_date"])
                days_until = (exp_date - today).days
                
                if 0 <= days_until <= days_ahead:
                    alert["days_until_expiration"] = days_until
                    
                    # Set urgency based on days until expiration
                    if days_until <= 30:
                        alert["urgency"] = "critical"
                    elif days_until <= 60:
                        alert["urgency"] = "high"
                    else:
                        alert["urgency"] = "medium"
                    
                    filtered_alerts.append(alert)
            
            self._cache_data(cache_key, filtered_alerts)
            return filtered_alerts
            
        except Exception as e:
            logger.error(f"Error getting contract alerts: {str(e)}")
            return []
    
    def get_regulatory_updates(self, hours_back: int = 168) -> List[Dict[str, Any]]:
        """
        Get regulatory framework updates.
        
        Args:
            hours_back (int): Number of hours to look back for updates (default: 7 days)
            
        Returns:
            List[Dict[str, Any]]: List of regulatory updates
        """
        cache_key = f"regulatory_updates_{hours_back}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Simulate regulatory updates
            updates = [
                {
                    "timestamp": (datetime.now() - timedelta(hours=24)).isoformat(),
                    "framework": "NIST 800-53",
                    "update_type": "control_enhancement",
                    "control_ids": ["AC-2(1)", "AC-2(2)"],
                    "title": "Enhanced Account Management Requirements",
                    "summary": "New guidance for automated account management and account monitoring",
                    "impact": "medium",
                    "affected_assets": 15,
                    "details": {
                        "requires_action": True,
                        "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
                        "guidance_url": "https://csrc.nist.gov/updates/ac-2-enhancements"
                    }
                },
                {
                    "timestamp": (datetime.now() - timedelta(hours=72)).isoformat(),
                    "framework": "HIPAA",
                    "update_type": "interpretation_clarification",
                    "control_ids": ["164.312(e)(1)"],
                    "title": "Transmission Security Clarification",
                    "summary": "Updated guidance on encryption requirements for PHI transmission",
                    "impact": "low",
                    "affected_assets": 8,
                    "details": {
                        "requires_action": False,
                        "guidance_url": "https://hhs.gov/hipaa/security-rule-updates"
                    }
                },
                {
                    "timestamp": (datetime.now() - timedelta(hours=120)).isoformat(),
                    "framework": "PCI DSS",
                    "update_type": "version_update",
                    "version": "4.0.1",
                    "title": "PCI DSS Version 4.0.1 Released",
                    "summary": "Minor updates and clarifications to version 4.0",
                    "impact": "low",
                    "affected_assets": 12,
                    "details": {
                        "requires_action": True,
                        "deadline": (datetime.now() + timedelta(days=180)).isoformat(),
                        "guidance_url": "https://pcisecuritystandards.org/documents/"
                    }
                }
            ]
            
            # Filter updates within time window
            filtered_updates = [
                update for update in updates
                if datetime.fromisoformat(update["timestamp"]) >= cutoff_time
            ]
            
            self._cache_data(cache_key, filtered_updates)
            return filtered_updates
            
        except Exception as e:
            logger.error(f"Error getting regulatory updates: {str(e)}")
            return []
    
    def get_security_incidents(self, hours_back: int = 72) -> List[Dict[str, Any]]:
        """
        Get security incidents and their compliance impact.
        
        Args:
            hours_back (int): Number of hours to look back for incidents
            
        Returns:
            List[Dict[str, Any]]: List of security incidents
        """
        cache_key = f"security_incidents_{hours_back}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Simulate security incidents
            incidents = [
                {
                    "timestamp": (datetime.now() - timedelta(hours=18)).isoformat(),
                    "incident_id": "INC-2023-001",
                    "severity": "medium",
                    "type": "unauthorized_access_attempt",
                    "affected_assets": ["ASSET-001", "ASSET-005"],
                    "status": "resolved",
                    "compliance_impact": {
                        "frameworks_affected": ["NIST 800-53", "PCI DSS"],
                        "controls_impacted": ["AC-3", "AC-7", "AU-2"],
                        "evidence_required": True,
                        "reporting_required": False
                    },
                    "details": {
                        "description": "Multiple failed login attempts detected on web server",
                        "resolution": "IP blocked, passwords reset, monitoring enhanced",
                        "response_time_minutes": 45
                    }
                },
                {
                    "timestamp": (datetime.now() - timedelta(hours=48)).isoformat(),
                    "incident_id": "INC-2023-002",
                    "severity": "low",
                    "type": "patch_compliance",
                    "affected_assets": ["ASSET-002", "ASSET-004"],
                    "status": "in_progress",
                    "compliance_impact": {
                        "frameworks_affected": ["NIST 800-53"],
                        "controls_impacted": ["CM-2", "SI-2"],
                        "evidence_required": True,
                        "reporting_required": False
                    },
                    "details": {
                        "description": "Critical security patches pending on endpoint devices",
                        "resolution": "Patches scheduled for next maintenance window",
                        "estimated_completion": (datetime.now() + timedelta(hours=24)).isoformat()
                    }
                }
            ]
            
            # Filter incidents within time window
            filtered_incidents = [
                incident for incident in incidents
                if datetime.fromisoformat(incident["timestamp"]) >= cutoff_time
            ]
            
            self._cache_data(cache_key, filtered_incidents)
            return filtered_incidents
            
        except Exception as e:
            logger.error(f"Error getting security incidents: {str(e)}")
            return []
    
    def get_trend_analysis(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Get trend analysis for the specified time period.
        
        Args:
            days_back (int): Number of days to analyze trends
            
        Returns:
            Dict[str, Any]: Trend analysis data
        """
        cache_key = f"trend_analysis_{days_back}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # Simulate trend analysis
            analysis = {
                "period": {
                    "start_date": (date.today() - timedelta(days=days_back)).isoformat(),
                    "end_date": date.today().isoformat(),
                    "days": days_back
                },
                "compliance_trends": {
                    "NIST 800-53": {
                        "direction": "improving",
                        "change_percentage": 3.8,
                        "key_improvements": ["Control Implementation Rate", "Evidence Quality"],
                        "areas_needing_attention": ["Risk Remediation"]
                    },
                    "HIPAA": {
                        "direction": "stable",
                        "change_percentage": 1.2,
                        "key_improvements": ["Assessment Coverage"],
                        "areas_needing_attention": []
                    },
                    "PCI DSS": {
                        "direction": "improving",
                        "change_percentage": 2.5,
                        "key_improvements": ["Asset Coverage", "Control Implementation Rate"],
                        "areas_needing_attention": ["Evidence Quality"]
                    }
                },
                "asset_trends": {
                    "new_assets_added": 3,
                    "assets_updated": 8,
                    "risk_level_improvements": 2,
                    "risk_level_degradations": 0
                },
                "incident_trends": {
                    "total_incidents": 5,
                    "resolved_incidents": 4,
                    "average_resolution_time_hours": 36,
                    "most_common_types": ["unauthorized_access_attempt", "patch_compliance"]
                },
                "contract_trends": {
                    "contracts_renewed": 1,
                    "contracts_expiring_soon": 2,
                    "cost_changes": {
                        "total_increase": 5000.00,
                        "percentage_change": 2.1
                    }
                }
            }
            
            self._cache_data(cache_key, analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting trend analysis: {str(e)}")
            return {}
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive intelligence summary combining all data sources.
        
        Returns:
            Dict[str, Any]: Intelligence summary
        """
        try:
            # Get data from all sources
            compliance_changes = self.get_compliance_changes(24)
            asset_changes = self.get_asset_changes(24)
            contract_alerts = self.get_contract_alerts(90)
            regulatory_updates = self.get_regulatory_updates(168)
            security_incidents = self.get_security_incidents(72)
            trend_analysis = self.get_trend_analysis(30)
            
            # Create summary
            summary = {
                "generated_at": datetime.now().isoformat(),
                "summary_period": "24 hours",
                "overall_status": "stable_improving",
                "key_metrics": {
                    "compliance_changes": len(compliance_changes),
                    "asset_changes": len(asset_changes),
                    "contract_alerts": len(contract_alerts),
                    "regulatory_updates": len(regulatory_updates),
                    "security_incidents": len(security_incidents)
                },
                "priority_items": [],
                "data": {
                    "compliance_changes": compliance_changes,
                    "asset_changes": asset_changes,
                    "contract_alerts": contract_alerts,
                    "regulatory_updates": regulatory_updates,
                    "security_incidents": security_incidents,
                    "trend_analysis": trend_analysis
                }
            }
            
            # Identify priority items
            priority_items = []
            
            # High-impact compliance changes
            for change in compliance_changes:
                if change.get("change_type") == "score_improvement" and change.get("change", 0) > 3:
                    priority_items.append({
                        "type": "compliance_improvement",
                        "priority": "high",
                        "title": f"{change['framework']} score improved by {change['change']}%",
                        "timestamp": change["timestamp"]
                    })
            
            # Critical contract alerts
            for alert in contract_alerts:
                if alert.get("urgency") == "critical":
                    priority_items.append({
                        "type": "contract_expiration",
                        "priority": "critical",
                        "title": f"Contract {alert['contract_name']} expires in {alert['days_until_expiration']} days",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Security incidents requiring action
            for incident in security_incidents:
                if incident.get("severity") == "high" or incident.get("status") == "in_progress":
                    priority_items.append({
                        "type": "security_incident",
                        "priority": "high",
                        "title": f"Security incident: {incident['type']} - {incident['status']}",
                        "timestamp": incident["timestamp"]
                    })
            
            # Regulatory updates requiring action
            for update in regulatory_updates:
                if update.get("details", {}).get("requires_action"):
                    priority_items.append({
                        "type": "regulatory_update",
                        "priority": "medium",
                        "title": f"{update['framework']}: {update['title']}",
                        "timestamp": update["timestamp"]
                    })
            
            # Sort priority items by timestamp (newest first)
            priority_items.sort(key=lambda x: x["timestamp"], reverse=True)
            summary["priority_items"] = priority_items[:10]  # Top 10 priority items
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting intelligence summary: {str(e)}")
            return {"error": str(e)}