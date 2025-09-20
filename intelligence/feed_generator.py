"""
Live intelligence feed generator for PolicyEdgeAI.

Generates real-time intelligence feeds from aggregated data.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import os
from .data_aggregator import DataAggregator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntelligenceFeedGenerator:
    """Generates live intelligence feeds from PolicyEdge data sources."""
    
    def __init__(self):
        """Initialize the feed generator."""
        self.data_aggregator = DataAggregator()
        self.feed_dir = os.path.join(os.getcwd(), "data", "intelligence", "feeds")
        os.makedirs(self.feed_dir, exist_ok=True)
    
    def generate_live_feed(self, feed_type: str = "comprehensive", limit: int = 50) -> Dict[str, Any]:
        """
        Generate a live intelligence feed.
        
        Args:
            feed_type (str): Type of feed to generate
                - "comprehensive": All intelligence types
                - "compliance": Compliance-focused
                - "security": Security-focused
                - "operations": Operations-focused
            limit (int): Maximum number of feed items
            
        Returns:
            Dict[str, Any]: Live intelligence feed
        """
        try:
            feed_items = []
            
            if feed_type in ["comprehensive", "compliance"]:
                feed_items.extend(self._get_compliance_feed_items())
            
            if feed_type in ["comprehensive", "security"]:
                feed_items.extend(self._get_security_feed_items())
            
            if feed_type in ["comprehensive", "operations"]:
                feed_items.extend(self._get_operations_feed_items())
            
            # Sort by timestamp (newest first)
            feed_items.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Apply limit
            if limit and limit > 0:
                feed_items = feed_items[:limit]
            
            feed = {
                "feed_type": feed_type,
                "generated_at": datetime.now().isoformat(),
                "total_items": len(feed_items),
                "items": feed_items,
                "metadata": {
                    "data_sources": ["compliance_scores", "asset_management", "contract_tracking", "regulatory_updates", "security_incidents"],
                    "update_frequency": "real-time",
                    "retention_period": "30 days"
                }
            }
            
            # Save feed to file
            self._save_feed(feed, feed_type)
            
            return feed
            
        except Exception as e:
            logger.error(f"Error generating live feed: {str(e)}")
            return {"error": str(e)}
    
    def _get_compliance_feed_items(self) -> List[Dict[str, Any]]:
        """Get compliance-related feed items."""
        items = []
        
        # Compliance score changes
        compliance_changes = self.data_aggregator.get_compliance_changes(24)
        for change in compliance_changes:
            items.append({
                "id": f"compliance_{change['timestamp']}_{change['framework']}",
                "timestamp": change["timestamp"],
                "type": "compliance_change",
                "category": "compliance",
                "priority": self._calculate_priority(change),
                "title": self._format_compliance_title(change),
                "summary": self._format_compliance_summary(change),
                "details": change,
                "tags": [change["framework"].lower().replace(" ", "_"), change["change_type"]],
                "action_required": change.get("change_type") == "score_decline",
                "related_assets": change.get("details", {}).get("related_assets", [])
            })
        
        # Regulatory updates
        regulatory_updates = self.data_aggregator.get_regulatory_updates(168)
        for update in regulatory_updates:
            items.append({
                "id": f"regulatory_{update['timestamp']}_{update['framework']}",
                "timestamp": update["timestamp"],
                "type": "regulatory_update",
                "category": "compliance",
                "priority": "medium" if update.get("impact") == "high" else "low",
                "title": f"{update['framework']}: {update['title']}",
                "summary": update["summary"],
                "details": update,
                "tags": [update["framework"].lower().replace(" ", "_"), update["update_type"]],
                "action_required": update.get("details", {}).get("requires_action", False),
                "related_assets": []
            })
        
        return items
    
    def _get_security_feed_items(self) -> List[Dict[str, Any]]:
        """Get security-related feed items."""
        items = []
        
        # Security incidents
        incidents = self.data_aggregator.get_security_incidents(72)
        for incident in incidents:
            items.append({
                "id": f"incident_{incident['incident_id']}",
                "timestamp": incident["timestamp"],
                "type": "security_incident",
                "category": "security",
                "priority": incident["severity"],
                "title": f"Security Incident: {incident['type'].replace('_', ' ').title()}",
                "summary": incident["details"]["description"],
                "details": incident,
                "tags": [incident["type"], incident["severity"], incident["status"]],
                "action_required": incident["status"] == "in_progress",
                "related_assets": incident.get("affected_assets", [])
            })
        
        # Asset risk level changes
        asset_changes = self.data_aggregator.get_asset_changes(24)
        for change in asset_changes:
            if change["change_type"] == "risk_level_change":
                items.append({
                    "id": f"asset_risk_{change['timestamp']}_{change['asset_id']}",
                    "timestamp": change["timestamp"],
                    "type": "asset_risk_change",
                    "category": "security",
                    "priority": "high" if change["new_risk"] == "critical" else "medium",
                    "title": f"Asset Risk Change: {change['asset_name']}",
                    "summary": f"Risk level changed from {change['old_risk']} to {change['new_risk']}",
                    "details": change,
                    "tags": ["asset_management", "risk_assessment", change["new_risk"]],
                    "action_required": change["new_risk"] in ["critical", "high"],
                    "related_assets": [change["asset_id"]]
                })
        
        return items
    
    def _get_operations_feed_items(self) -> List[Dict[str, Any]]:
        """Get operations-related feed items."""
        items = []
        
        # Asset changes (new assets, status changes)
        asset_changes = self.data_aggregator.get_asset_changes(24)
        for change in asset_changes:
            if change["change_type"] in ["new_asset", "status_change"]:
                items.append({
                    "id": f"asset_{change['timestamp']}_{change['asset_id']}",
                    "timestamp": change["timestamp"],
                    "type": "asset_change",
                    "category": "operations",
                    "priority": "low" if change["change_type"] == "new_asset" else "medium",
                    "title": self._format_asset_title(change),
                    "summary": self._format_asset_summary(change),
                    "details": change,
                    "tags": ["asset_management", change["change_type"]],
                    "action_required": change["change_type"] == "status_change" and change.get("new_status") == "maintenance",
                    "related_assets": [change["asset_id"]]
                })
        
        # Contract alerts
        contract_alerts = self.data_aggregator.get_contract_alerts(90)
        for alert in contract_alerts:
            items.append({
                "id": f"contract_{alert['contract_id']}",
                "timestamp": datetime.now().isoformat(),
                "type": "contract_alert",
                "category": "operations",
                "priority": alert["urgency"],
                "title": f"Contract Expiring: {alert['contract_name']}",
                "summary": f"Contract expires in {alert['days_until_expiration']} days (${alert['annual_cost']:,.2f}/year)",
                "details": alert,
                "tags": ["contract_management", "expiration", alert["urgency"]],
                "action_required": alert["urgency"] in ["critical", "high"],
                "related_assets": [alert["asset_id"]]
            })
        
        return items
    
    def _calculate_priority(self, change: Dict[str, Any]) -> str:
        """Calculate priority for a compliance change."""
        if change.get("change_type") == "score_improvement":
            change_amount = abs(change.get("change", 0))
            if change_amount >= 5:
                return "high"
            elif change_amount >= 2:
                return "medium"
            else:
                return "low"
        elif change.get("change_type") == "score_decline":
            return "high"
        elif change.get("change_type") == "control_implementation":
            return "medium"
        else:
            return "low"
    
    def _format_compliance_title(self, change: Dict[str, Any]) -> str:
        """Format title for compliance change."""
        if change.get("change_type") == "score_improvement":
            return f"{change['framework']} Score Improved (+{change['change']}%)"
        elif change.get("change_type") == "score_decline":
            return f"{change['framework']} Score Declined ({change['change']}%)"
        elif change.get("change_type") == "control_implementation":
            return f"Control Implemented: {change.get('control_id', 'Unknown')}"
        elif change.get("change_type") == "risk_level_change":
            return f"Risk Level Updated: {change.get('control_id', 'Unknown')}"
        else:
            return f"{change['framework']} Update"
    
    def _format_compliance_summary(self, change: Dict[str, Any]) -> str:
        """Format summary for compliance change."""
        if change.get("change_type") == "score_improvement":
            metrics = change.get("details", {}).get("improved_metrics", [])
            metrics_text = ", ".join(metrics) if metrics else "multiple areas"
            return f"Compliance score increased from {change['old_score']}% to {change['new_score']}% due to improvements in {metrics_text}"
        elif change.get("change_type") == "control_implementation":
            control_name = change.get("details", {}).get("control_name", change.get("control_id", "Unknown"))
            return f"Control '{control_name}' status changed from {change['old_status']} to {change['new_status']}"
        elif change.get("change_type") == "risk_level_change":
            return f"Risk level changed from {change['old_risk']} to {change['new_risk']}: {change.get('details', {}).get('reason', 'No reason provided')}"
        else:
            return change.get("summary", "Compliance update")
    
    def _format_asset_title(self, change: Dict[str, Any]) -> str:
        """Format title for asset change."""
        if change["change_type"] == "new_asset":
            return f"New Asset Added: {change['asset_name']}"
        elif change["change_type"] == "status_change":
            return f"Asset Status Change: {change['asset_name']}"
        else:
            return f"Asset Update: {change['asset_name']}"
    
    def _format_asset_summary(self, change: Dict[str, Any]) -> str:
        """Format summary for asset change."""
        if change["change_type"] == "new_asset":
            return f"New {change['asset_type']} added to {change.get('details', {}).get('department', 'organization')} with {change['risk_level']} risk level"
        elif change["change_type"] == "status_change":
            reason = change.get("details", {}).get("reason", "No reason provided")
            return f"Status changed from {change['old_status']} to {change['new_status']}: {reason}"
        else:
            return "Asset has been updated"
    
    def _save_feed(self, feed: Dict[str, Any], feed_type: str) -> None:
        """Save feed to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"feed_{feed_type}_{timestamp}.json"
            filepath = os.path.join(self.feed_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(feed, f, indent=2, default=str)
            
            # Keep only the latest 10 feeds per type
            self._cleanup_old_feeds(feed_type)
            
        except Exception as e:
            logger.error(f"Error saving feed: {str(e)}")
    
    def _cleanup_old_feeds(self, feed_type: str) -> None:
        """Clean up old feed files, keeping only the latest 10."""
        try:
            # Get all feed files for this type
            feed_files = [
                f for f in os.listdir(self.feed_dir)
                if f.startswith(f"feed_{feed_type}_") and f.endswith(".json")
            ]
            
            # Sort by modification time (newest first)
            feed_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(self.feed_dir, f)),
                reverse=True
            )
            
            # Remove files beyond the limit
            for old_file in feed_files[10:]:
                os.remove(os.path.join(self.feed_dir, old_file))
                
        except Exception as e:
            logger.error(f"Error cleaning up old feeds: {str(e)}")
    
    def get_feed_history(self, feed_type: str = "comprehensive", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get historical feeds of a specific type.
        
        Args:
            feed_type (str): Type of feed to retrieve
            limit (int): Maximum number of feeds to return
            
        Returns:
            List[Dict[str, Any]]: List of historical feeds
        """
        try:
            # Get all feed files for this type
            feed_files = [
                f for f in os.listdir(self.feed_dir)
                if f.startswith(f"feed_{feed_type}_") and f.endswith(".json")
            ]
            
            # Sort by modification time (newest first)
            feed_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(self.feed_dir, f)),
                reverse=True
            )
            
            # Load and return feeds
            feeds = []
            for feed_file in feed_files[:limit]:
                try:
                    with open(os.path.join(self.feed_dir, feed_file), 'r') as f:
                        feed = json.load(f)
                        feeds.append(feed)
                except Exception as e:
                    logger.error(f"Error loading feed file {feed_file}: {str(e)}")
            
            return feeds
            
        except Exception as e:
            logger.error(f"Error getting feed history: {str(e)}")
            return []
    
    def get_feed_item_details(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific feed item.
        
        Args:
            item_id (str): Unique identifier for the feed item
            
        Returns:
            Optional[Dict[str, Any]]: Feed item details if found
        """
        try:
            # Search through recent feeds for the item
            for feed_type in ["comprehensive", "compliance", "security", "operations"]:
                feeds = self.get_feed_history(feed_type, 5)
                for feed in feeds:
                    for item in feed.get("items", []):
                        if item.get("id") == item_id:
                            return item
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting feed item details: {str(e)}")
            return None
    
    def get_feed_metrics(self, feed_type: str = "comprehensive", hours_back: int = 24) -> Dict[str, Any]:
        """
        Get metrics about feed activity.
        
        Args:
            feed_type (str): Type of feed to analyze
            hours_back (int): Number of hours to look back
            
        Returns:
            Dict[str, Any]: Feed metrics
        """
        try:
            # Generate current feed to get latest data
            current_feed = self.generate_live_feed(feed_type, 1000)
            
            if "error" in current_feed:
                return current_feed
            
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            recent_items = [
                item for item in current_feed.get("items", [])
                if datetime.fromisoformat(item["timestamp"]) >= cutoff_time
            ]
            
            # Calculate metrics
            metrics = {
                "period": {
                    "hours_back": hours_back,
                    "start_time": cutoff_time.isoformat(),
                    "end_time": datetime.now().isoformat()
                },
                "total_items": len(recent_items),
                "by_category": {},
                "by_priority": {},
                "by_type": {},
                "action_required": 0,
                "related_assets": set()
            }
            
            for item in recent_items:
                # Count by category
                category = item.get("category", "unknown")
                metrics["by_category"][category] = metrics["by_category"].get(category, 0) + 1
                
                # Count by priority
                priority = item.get("priority", "unknown")
                metrics["by_priority"][priority] = metrics["by_priority"].get(priority, 0) + 1
                
                # Count by type
                item_type = item.get("type", "unknown")
                metrics["by_type"][item_type] = metrics["by_type"].get(item_type, 0) + 1
                
                # Count items requiring action
                if item.get("action_required"):
                    metrics["action_required"] += 1
                
                # Collect related assets
                metrics["related_assets"].update(item.get("related_assets", []))
            
            # Convert set to list for JSON serialization
            metrics["related_assets"] = list(metrics["related_assets"])
            metrics["unique_assets_affected"] = len(metrics["related_assets"])
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting feed metrics: {str(e)}")
            return {"error": str(e)}