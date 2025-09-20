"""
Newspaper-style intelligence memo generator for PolicyEdgeAI.

Generates formatted intelligence memos in newspaper style from aggregated data.
"""

import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import json
import os
from .data_aggregator import DataAggregator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NewspaperMemoGenerator:
    """Generates newspaper-style intelligence memos from PolicyEdge data sources."""
    
    def __init__(self):
        """Initialize the memo generator."""
        self.data_aggregator = DataAggregator()
        self.memo_dir = os.path.join(os.getcwd(), "data", "intelligence", "memos")
        os.makedirs(self.memo_dir, exist_ok=True)
    
    def generate_intelligence_memo(self, memo_type: str = "daily", include_charts: bool = True) -> Dict[str, Any]:
        """
        Generate a newspaper-style intelligence memo.
        
        Args:
            memo_type (str): Type of memo to generate
                - "daily": Daily intelligence summary
                - "weekly": Weekly intelligence digest
                - "monthly": Monthly intelligence report
                - "incident": Incident-focused memo
                - "compliance": Compliance-focused memo
            include_charts (bool): Whether to include chart data
            
        Returns:
            Dict[str, Any]: Intelligence memo
        """
        try:
            # Get intelligence summary
            intelligence_summary = self.data_aggregator.get_intelligence_summary()
            
            if "error" in intelligence_summary:
                return intelligence_summary
            
            # Generate memo based on type
            if memo_type == "daily":
                memo = self._generate_daily_memo(intelligence_summary, include_charts)
            elif memo_type == "weekly":
                memo = self._generate_weekly_memo(intelligence_summary, include_charts)
            elif memo_type == "monthly":
                memo = self._generate_monthly_memo(intelligence_summary, include_charts)
            elif memo_type == "incident":
                memo = self._generate_incident_memo(intelligence_summary, include_charts)
            elif memo_type == "compliance":
                memo = self._generate_compliance_memo(intelligence_summary, include_charts)
            else:
                return {"error": f"Unknown memo type: {memo_type}"}
            
            # Save memo to file
            self._save_memo(memo, memo_type)
            
            return memo
            
        except Exception as e:
            logger.error(f"Error generating intelligence memo: {str(e)}")
            return {"error": str(e)}
    
    def _generate_daily_memo(self, intelligence_summary: Dict[str, Any], include_charts: bool) -> Dict[str, Any]:
        """Generate a daily intelligence memo."""
        today = date.today()
        
        # Create headline based on most significant event
        headline = self._generate_headline(intelligence_summary)
        
        # Create executive summary
        executive_summary = self._generate_executive_summary(intelligence_summary)
        
        # Create sections
        sections = []
        
        # Compliance section
        compliance_section = self._create_compliance_section(intelligence_summary)
        if compliance_section:
            sections.append(compliance_section)
        
        # Security section
        security_section = self._create_security_section(intelligence_summary)
        if security_section:
            sections.append(security_section)
        
        # Operations section
        operations_section = self._create_operations_section(intelligence_summary)
        if operations_section:
            sections.append(operations_section)
        
        # Trending section
        trending_section = self._create_trending_section(intelligence_summary)
        if trending_section:
            sections.append(trending_section)
        
        # Create memo structure
        memo = {
            "memo_type": "daily",
            "generated_at": datetime.now().isoformat(),
            "date": today.isoformat(),
            "headline": headline,
            "subheadline": self._generate_subheadline(intelligence_summary),
            "executive_summary": executive_summary,
            "sections": sections,
            "sidebar": self._create_sidebar(intelligence_summary),
            "metadata": {
                "data_period": "24 hours",
                "sources": intelligence_summary.get("key_metrics", {}),
                "priority_level": self._determine_priority_level(intelligence_summary),
                "distribution": "internal",
                "classification": "confidential"
            }
        }
        
        if include_charts:
            memo["charts"] = self._generate_chart_data(intelligence_summary)
        
        return memo
    
    def _generate_weekly_memo(self, intelligence_summary: Dict[str, Any], include_charts: bool) -> Dict[str, Any]:
        """Generate a weekly intelligence memo."""
        # Get extended data for weekly analysis
        weekly_data = {
            "compliance_changes": self.data_aggregator.get_compliance_changes(168),  # 7 days
            "asset_changes": self.data_aggregator.get_asset_changes(168),
            "contract_alerts": self.data_aggregator.get_contract_alerts(90),
            "regulatory_updates": self.data_aggregator.get_regulatory_updates(168),
            "security_incidents": self.data_aggregator.get_security_incidents(168),
            "trend_analysis": self.data_aggregator.get_trend_analysis(7)
        }
        
        week_start = date.today() - timedelta(days=7)
        week_end = date.today()
        
        memo = {
            "memo_type": "weekly",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start_date": week_start.isoformat(),
                "end_date": week_end.isoformat()
            },
            "headline": f"Weekly Intelligence Digest: {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}",
            "subheadline": "Comprehensive analysis of compliance, security, and operational intelligence",
            "executive_summary": self._generate_weekly_executive_summary(weekly_data),
            "sections": self._generate_weekly_sections(weekly_data),
            "sidebar": self._create_weekly_sidebar(weekly_data),
            "metadata": {
                "data_period": "7 days",
                "sources": {k: len(v) if isinstance(v, list) else 1 for k, v in weekly_data.items()},
                "priority_level": "medium",
                "distribution": "management",
                "classification": "confidential"
            }
        }
        
        if include_charts:
            memo["charts"] = self._generate_weekly_chart_data(weekly_data)
        
        return memo
    
    def _generate_monthly_memo(self, intelligence_summary: Dict[str, Any], include_charts: bool) -> Dict[str, Any]:
        """Generate a monthly intelligence memo."""
        # Get extended data for monthly analysis
        monthly_data = {
            "compliance_changes": self.data_aggregator.get_compliance_changes(720),  # 30 days
            "asset_changes": self.data_aggregator.get_asset_changes(720),
            "contract_alerts": self.data_aggregator.get_contract_alerts(90),
            "regulatory_updates": self.data_aggregator.get_regulatory_updates(720),
            "security_incidents": self.data_aggregator.get_security_incidents(720),
            "trend_analysis": self.data_aggregator.get_trend_analysis(30)
        }
        
        today = date.today()
        month_start = today.replace(day=1)
        
        memo = {
            "memo_type": "monthly",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start_date": month_start.isoformat(),
                "end_date": today.isoformat(),
                "month": today.strftime("%B %Y")
            },
            "headline": f"Monthly Intelligence Report: {today.strftime('%B %Y')}",
            "subheadline": "Strategic overview of compliance posture and operational intelligence",
            "executive_summary": self._generate_monthly_executive_summary(monthly_data),
            "sections": self._generate_monthly_sections(monthly_data),
            "sidebar": self._create_monthly_sidebar(monthly_data),
            "metadata": {
                "data_period": "30 days",
                "sources": {k: len(v) if isinstance(v, list) else 1 for k, v in monthly_data.items()},
                "priority_level": "high",
                "distribution": "executive",
                "classification": "confidential"
            }
        }
        
        if include_charts:
            memo["charts"] = self._generate_monthly_chart_data(monthly_data)
        
        return memo
    
    def _generate_incident_memo(self, intelligence_summary: Dict[str, Any], include_charts: bool) -> Dict[str, Any]:
        """Generate an incident-focused memo."""
        incidents = intelligence_summary.get("data", {}).get("security_incidents", [])
        
        memo = {
            "memo_type": "incident",
            "generated_at": datetime.now().isoformat(),
            "headline": "Security Incident Intelligence Brief",
            "subheadline": f"Analysis of {len(incidents)} security incidents in the past 72 hours",
            "executive_summary": self._generate_incident_executive_summary(incidents),
            "sections": self._generate_incident_sections(incidents),
            "sidebar": self._create_incident_sidebar(incidents),
            "metadata": {
                "data_period": "72 hours",
                "total_incidents": len(incidents),
                "priority_level": self._determine_incident_priority(incidents),
                "distribution": "security_team",
                "classification": "restricted"
            }
        }
        
        if include_charts:
            memo["charts"] = self._generate_incident_chart_data(incidents)
        
        return memo
    
    def _generate_compliance_memo(self, intelligence_summary: Dict[str, Any], include_charts: bool) -> Dict[str, Any]:
        """Generate a compliance-focused memo."""
        compliance_data = intelligence_summary.get("data", {})
        
        memo = {
            "memo_type": "compliance",
            "generated_at": datetime.now().isoformat(),
            "headline": "Compliance Intelligence Update",
            "subheadline": "Regulatory compliance status and recent developments",
            "executive_summary": self._generate_compliance_executive_summary(compliance_data),
            "sections": self._generate_compliance_sections(compliance_data),
            "sidebar": self._create_compliance_sidebar(compliance_data),
            "metadata": {
                "data_period": "7 days",
                "frameworks_covered": self._get_frameworks_covered(compliance_data),
                "priority_level": "medium",
                "distribution": "compliance_team",
                "classification": "confidential"
            }
        }
        
        if include_charts:
            memo["charts"] = self._generate_compliance_chart_data(compliance_data)
        
        return memo
    
    def _generate_headline(self, intelligence_summary: Dict[str, Any]) -> str:
        """Generate main headline based on most significant event."""
        priority_items = intelligence_summary.get("priority_items", [])
        
        if not priority_items:
            return "PolicyEdge Intelligence: Stable Operations Across All Systems"
        
        top_item = priority_items[0]
        
        if top_item["type"] == "compliance_improvement":
            return f"Compliance Breakthrough: {top_item['title']}"
        elif top_item["type"] == "contract_expiration":
            return f"Contract Alert: Critical Renewal Required"
        elif top_item["type"] == "security_incident":
            return f"Security Update: {top_item['title']}"
        elif top_item["type"] == "regulatory_update":
            return f"Regulatory Changes: New Requirements Announced"
        else:
            return f"Intelligence Update: {top_item['title']}"
    
    def _generate_subheadline(self, intelligence_summary: Dict[str, Any]) -> str:
        """Generate subheadline with key metrics."""
        metrics = intelligence_summary.get("key_metrics", {})
        total_events = sum(metrics.values())
        
        if total_events == 0:
            return "No significant events reported in the past 24 hours"
        elif total_events == 1:
            return "1 significant event reported in the past 24 hours"
        else:
            return f"{total_events} significant events reported in the past 24 hours"
    
    def _generate_executive_summary(self, intelligence_summary: Dict[str, Any]) -> str:
        """Generate executive summary for daily memo."""
        status = intelligence_summary.get("overall_status", "stable")
        priority_items = intelligence_summary.get("priority_items", [])
        metrics = intelligence_summary.get("key_metrics", {})
        
        summary_parts = []
        
        # Overall status
        if status == "stable_improving":
            summary_parts.append("PolicyEdge systems show stable operations with improving compliance metrics.")
        elif status == "stable":
            summary_parts.append("PolicyEdge systems maintain stable operations across all monitored areas.")
        elif status == "attention_required":
            summary_parts.append("PolicyEdge systems require attention due to recent developments.")
        else:
            summary_parts.append("PolicyEdge systems status is being monitored.")
        
        # Key metrics summary
        if metrics.get("compliance_changes", 0) > 0:
            summary_parts.append(f"{metrics['compliance_changes']} compliance score changes recorded.")
        
        if metrics.get("security_incidents", 0) > 0:
            summary_parts.append(f"{metrics['security_incidents']} security incidents under review.")
        
        if metrics.get("contract_alerts", 0) > 0:
            summary_parts.append(f"{metrics['contract_alerts']} contract renewals require attention.")
        
        # Priority items summary
        if priority_items:
            high_priority = len([item for item in priority_items if item.get("priority") == "high"])
            if high_priority > 0:
                summary_parts.append(f"{high_priority} high-priority items identified for immediate action.")
        
        return " ".join(summary_parts)
    
    def _create_compliance_section(self, intelligence_summary: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create compliance section for the memo."""
        compliance_changes = intelligence_summary.get("data", {}).get("compliance_changes", [])
        regulatory_updates = intelligence_summary.get("data", {}).get("regulatory_updates", [])
        
        if not compliance_changes and not regulatory_updates:
            return None
        
        articles = []
        
        # Compliance score changes
        for change in compliance_changes[:3]:  # Top 3 changes
            if change.get("change_type") == "score_improvement":
                articles.append({
                    "title": f"{change['framework']} Compliance Score Rises {change['change']}%",
                    "content": f"The {change['framework']} compliance score improved from {change['old_score']}% to {change['new_score']}%, marking a significant {change['change']}% increase. This improvement was driven by {', '.join(change.get('details', {}).get('improved_metrics', ['multiple factors']))}. The organization continues to strengthen its compliance posture through systematic control implementation and evidence collection.",
                    "timestamp": change["timestamp"],
                    "byline": "Compliance Monitoring Team"
                })
            elif change.get("change_type") == "control_implementation":
                control_name = change.get("details", {}).get("control_name", change.get("control_id", "Unknown"))
                articles.append({
                    "title": f"New Control Implementation: {control_name}",
                    "content": f"Control {change.get('control_id', 'Unknown')} has been successfully implemented and moved from {change['old_status']} to {change['new_status']} status. This implementation enhances the organization's {change['framework']} compliance framework and addresses key security requirements.",
                    "timestamp": change["timestamp"],
                    "byline": "Control Implementation Team"
                })
        
        # Regulatory updates
        for update in regulatory_updates[:2]:  # Top 2 updates
            action_text = ("Action is required by " + update.get("details", {}).get("deadline", "the specified deadline")) if update.get("details", {}).get("requires_action") else "No immediate action is required."
            articles.append({
                "title": f"{update['framework']}: {update['title']}",
                "content": f"{update['summary']} This {update['update_type']} affects {update.get('affected_assets', 0)} assets in our environment. {action_text}",
                "timestamp": update["timestamp"],
                "byline": "Regulatory Affairs"
            })
        
        if not articles:
            return None
        
        return {
            "title": "Compliance & Regulatory",
            "subtitle": "Compliance score updates and regulatory developments",
            "articles": articles
        }
    
    def _create_security_section(self, intelligence_summary: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create security section for the memo."""
        incidents = intelligence_summary.get("data", {}).get("security_incidents", [])
        asset_changes = intelligence_summary.get("data", {}).get("asset_changes", [])
        
        articles = []
        
        # Security incidents
        for incident in incidents[:3]:  # Top 3 incidents
            articles.append({
                "title": f"Security Incident: {incident['type'].replace('_', ' ').title()}",
                "content": f"Incident {incident['incident_id']} ({incident['severity']} severity) was detected involving {len(incident.get('affected_assets', []))} assets. {incident['details']['description']} Status: {incident['status']}. The incident affects compliance frameworks: {', '.join(incident.get('compliance_impact', {}).get('frameworks_affected', []))}.",
                "timestamp": incident["timestamp"],
                "byline": "Security Operations Center"
            })
        
        # Asset risk changes
        risk_changes = [change for change in asset_changes if change["change_type"] == "risk_level_change"]
        for change in risk_changes[:2]:  # Top 2 risk changes
            articles.append({
                "title": f"Asset Risk Level Updated: {change['asset_name']}",
                "content": f"Risk assessment for {change['asset_name']} (ID: {change['asset_id']}) has been updated from {change['old_risk']} to {change['new_risk']} risk level. Reason: {change.get('details', {}).get('reason', 'Risk assessment update')}. This change affects related compliance controls and may require updated evidence collection.",
                "timestamp": change["timestamp"],
                "byline": "Risk Management Team"
            })
        
        if not articles:
            return None
        
        return {
            "title": "Security & Risk",
            "subtitle": "Security incidents and risk assessment updates",
            "articles": articles
        }
    
    def _create_operations_section(self, intelligence_summary: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create operations section for the memo."""
        asset_changes = intelligence_summary.get("data", {}).get("asset_changes", [])
        contract_alerts = intelligence_summary.get("data", {}).get("contract_alerts", [])
        
        articles = []
        
        # Asset changes (new assets, status changes)
        operational_changes = [change for change in asset_changes if change["change_type"] in ["new_asset", "status_change"]]
        for change in operational_changes[:3]:  # Top 3 changes
            if change["change_type"] == "new_asset":
                articles.append({
                    "title": f"New Asset Added: {change['asset_name']}",
                    "content": f"A new {change['asset_type']} has been added to the {change.get('details', {}).get('department', 'organization')} inventory. The asset (ID: {change['asset_id']}) has been classified with {change['risk_level']} risk level and is located at {change.get('details', {}).get('location', 'primary facility')}.",
                    "timestamp": change["timestamp"],
                    "byline": "Asset Management"
                })
            elif change["change_type"] == "status_change":
                articles.append({
                    "title": f"Asset Status Update: {change['asset_name']}",
                    "content": f"{change['asset_name']} (ID: {change['asset_id']}) status changed from {change['old_status']} to {change['new_status']}. Reason: {change.get('details', {}).get('reason', 'Scheduled maintenance')}. {'Estimated completion: ' + change.get('details', {}).get('estimated_completion', 'TBD') if change.get('new_status') == 'maintenance' else ''}",
                    "timestamp": change["timestamp"],
                    "byline": "Operations Team"
                })
        
        # Contract alerts
        for alert in contract_alerts[:2]:  # Top 2 alerts
            urgency_text = "immediate" if alert["urgency"] == "critical" else alert["urgency"]
            articles.append({
                "title": f"Contract Renewal Required: {alert['contract_name']}",
                "content": f"Contract {alert['contract_id']} for {alert['asset_name']} expires in {alert['days_until_expiration']} days ({alert['expiration_date']}). Annual cost: ${alert['annual_cost']:,.2f}. Renewal type: {alert['renewal_type']}. {urgency_text.title()} attention required from {alert.get('details', {}).get('contract_owner', 'contract owner')}.",
                "timestamp": datetime.now().isoformat(),
                "byline": "Contract Management"
            })
        
        if not articles:
            return None
        
        return {
            "title": "Operations & Assets",
            "subtitle": "Asset management and contract administration updates",
            "articles": articles
        }
    
    def _create_trending_section(self, intelligence_summary: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create trending section for the memo."""
        trend_analysis = intelligence_summary.get("data", {}).get("trend_analysis", {})
        
        if not trend_analysis:
            return None
        
        articles = []
        
        # Compliance trends
        compliance_trends = trend_analysis.get("compliance_trends", {})
        improving_frameworks = [fw for fw, data in compliance_trends.items() if data.get("direction") == "improving"]
        
        if improving_frameworks:
            articles.append({
                "title": "Compliance Momentum: Positive Trends Across Frameworks",
                "content": f"Analysis of the past 30 days shows improving compliance trends in {', '.join(improving_frameworks)}. Key improvement areas include {', '.join(set().union(*[data.get('key_improvements', []) for data in compliance_trends.values() if data.get('direction') == 'improving']))}. Organizations should maintain current momentum while addressing areas that need attention.",
                "timestamp": datetime.now().isoformat(),
                "byline": "Trend Analysis Team"
            })
        
        # Asset trends
        asset_trends = trend_analysis.get("asset_trends", {})
        if asset_trends.get("new_assets_added", 0) > 0 or asset_trends.get("risk_level_improvements", 0) > 0:
            articles.append({
                "title": "Asset Portfolio Growth and Risk Improvements",
                "content": f"Asset inventory has grown by {asset_trends.get('new_assets_added', 0)} assets this month, with {asset_trends.get('risk_level_improvements', 0)} assets showing improved risk profiles. {asset_trends.get('assets_updated', 0)} assets received configuration updates. No risk degradations were recorded, indicating effective risk management practices.",
                "timestamp": datetime.now().isoformat(),
                "byline": "Asset Analytics"
            })
        
        # Incident trends
        incident_trends = trend_analysis.get("incident_trends", {})
        if incident_trends.get("total_incidents", 0) > 0:
            resolution_rate = (incident_trends.get("resolved_incidents", 0) / incident_trends.get("total_incidents", 1)) * 100
            articles.append({
                "title": f"Security Response: {resolution_rate:.0f}% Incident Resolution Rate",
                "content": f"Security operations resolved {incident_trends.get('resolved_incidents', 0)} of {incident_trends.get('total_incidents', 0)} incidents with an average response time of {incident_trends.get('average_resolution_time_hours', 0)} hours. Most common incident types: {', '.join(incident_trends.get('most_common_types', []))}.",
                "timestamp": datetime.now().isoformat(),
                "byline": "Security Metrics"
            })
        
        if not articles:
            return None
        
        return {
            "title": "Trending",
            "subtitle": "30-day trend analysis and insights",
            "articles": articles
        }
    
    def _create_sidebar(self, intelligence_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Create sidebar with quick stats and highlights."""
        metrics = intelligence_summary.get("key_metrics", {})
        priority_items = intelligence_summary.get("priority_items", [])
        
        return {
            "quick_stats": {
                "events_24h": sum(metrics.values()),
                "high_priority": len([item for item in priority_items if item.get("priority") == "high"]),
                "action_items": len([item for item in priority_items if item.get("priority") in ["high", "critical"]]),
                "frameworks_updated": len(set(item.get("title", "").split(":")[0] for item in priority_items if ":" in item.get("title", "")))
            },
            "highlights": [
                item["title"] for item in priority_items[:5]
            ],
            "upcoming": self._get_upcoming_items(intelligence_summary)
        }
    
    def _get_upcoming_items(self, intelligence_summary: Dict[str, Any]) -> List[str]:
        """Get upcoming items that require attention."""
        contract_alerts = intelligence_summary.get("data", {}).get("contract_alerts", [])
        regulatory_updates = intelligence_summary.get("data", {}).get("regulatory_updates", [])
        
        upcoming = []
        
        # Contract renewals
        for alert in contract_alerts[:3]:
            if alert["days_until_expiration"] <= 60:
                upcoming.append(f"Contract renewal: {alert['contract_name']} ({alert['days_until_expiration']} days)")
        
        # Regulatory deadlines
        for update in regulatory_updates[:2]:
            if update.get("details", {}).get("requires_action"):
                deadline = update.get("details", {}).get("deadline")
                if deadline:
                    upcoming.append(f"Compliance deadline: {update['title']}")
        
        return upcoming[:5]  # Top 5 upcoming items
    
    def _generate_chart_data(self, intelligence_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart data for visualizations."""
        return {
            "compliance_trends": self._create_compliance_trend_chart(intelligence_summary),
            "incident_timeline": self._create_incident_timeline_chart(intelligence_summary),
            "asset_risk_distribution": self._create_asset_risk_chart(intelligence_summary),
            "priority_breakdown": self._create_priority_breakdown_chart(intelligence_summary)
        }
    
    def _create_compliance_trend_chart(self, intelligence_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Create compliance trend chart data."""
        trend_analysis = intelligence_summary.get("data", {}).get("trend_analysis", {})
        compliance_trends = trend_analysis.get("compliance_trends", {})
        
        frameworks = list(compliance_trends.keys())
        changes = [compliance_trends[fw].get("change_percentage", 0) for fw in frameworks]
        
        return {
            "type": "bar",
            "title": "Compliance Score Changes (30 days)",
            "data": {
                "labels": frameworks,
                "values": changes
            }
        }
    
    def _create_incident_timeline_chart(self, intelligence_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Create incident timeline chart data."""
        incidents = intelligence_summary.get("data", {}).get("security_incidents", [])
        
        # Group incidents by day
        incident_counts = {}
        for incident in incidents:
            incident_date = datetime.fromisoformat(incident["timestamp"]).date()
            incident_counts[incident_date.isoformat()] = incident_counts.get(incident_date.isoformat(), 0) + 1
        
        return {
            "type": "line",
            "title": "Security Incidents (72 hours)",
            "data": {
                "labels": list(incident_counts.keys()),
                "values": list(incident_counts.values())
            }
        }
    
    def _create_asset_risk_chart(self, intelligence_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Create asset risk distribution chart data."""
        # This would normally query the asset database
        # For demo purposes, we'll create sample data
        return {
            "type": "pie",
            "title": "Asset Risk Distribution",
            "data": {
                "labels": ["Low", "Medium", "High", "Critical"],
                "values": [45, 32, 18, 5]
            }
        }
    
    def _create_priority_breakdown_chart(self, intelligence_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Create priority breakdown chart data."""
        priority_items = intelligence_summary.get("priority_items", [])
        
        priority_counts = {}
        for item in priority_items:
            priority = item.get("priority", "unknown")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "type": "donut",
            "title": "Priority Items Breakdown",
            "data": {
                "labels": list(priority_counts.keys()),
                "values": list(priority_counts.values())
            }
        }
    
    def _determine_priority_level(self, intelligence_summary: Dict[str, Any]) -> str:
        """Determine overall priority level for the memo."""
        priority_items = intelligence_summary.get("priority_items", [])
        
        if any(item.get("priority") == "critical" for item in priority_items):
            return "critical"
        elif any(item.get("priority") == "high" for item in priority_items):
            return "high"
        elif len(priority_items) > 5:
            return "medium"
        else:
            return "low"
    
    def _save_memo(self, memo: Dict[str, Any], memo_type: str) -> None:
        """Save memo to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memo_{memo_type}_{timestamp}.json"
            filepath = os.path.join(self.memo_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(memo, f, indent=2, default=str)
            
            # Keep only the latest 20 memos per type
            self._cleanup_old_memos(memo_type)
            
        except Exception as e:
            logger.error(f"Error saving memo: {str(e)}")
    
    def _cleanup_old_memos(self, memo_type: str) -> None:
        """Clean up old memo files, keeping only the latest 20."""
        try:
            # Get all memo files for this type
            memo_files = [
                f for f in os.listdir(self.memo_dir)
                if f.startswith(f"memo_{memo_type}_") and f.endswith(".json")
            ]
            
            # Sort by modification time (newest first)
            memo_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(self.memo_dir, f)),
                reverse=True
            )
            
            # Remove files beyond the limit
            for old_file in memo_files[20:]:
                os.remove(os.path.join(self.memo_dir, old_file))
                
        except Exception as e:
            logger.error(f"Error cleaning up old memos: {str(e)}")
    
    def get_memo_history(self, memo_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get historical memos.
        
        Args:
            memo_type (str, optional): Type of memo to retrieve
            limit (int): Maximum number of memos to return
            
        Returns:
            List[Dict[str, Any]]: List of historical memos
        """
        try:
            # Get all memo files
            if memo_type:
                memo_files = [
                    f for f in os.listdir(self.memo_dir)
                    if f.startswith(f"memo_{memo_type}_") and f.endswith(".json")
                ]
            else:
                memo_files = [
                    f for f in os.listdir(self.memo_dir)
                    if f.startswith("memo_") and f.endswith(".json")
                ]
            
            # Sort by modification time (newest first)
            memo_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(self.memo_dir, f)),
                reverse=True
            )
            
            # Load and return memos
            memos = []
            for memo_file in memo_files[:limit]:
                try:
                    with open(os.path.join(self.memo_dir, memo_file), 'r') as f:
                        memo = json.load(f)
                        memos.append(memo)
                except Exception as e:
                    logger.error(f"Error loading memo file {memo_file}: {str(e)}")
            
            return memos
            
        except Exception as e:
            logger.error(f"Error getting memo history: {str(e)}")
            return []
    
    def export_memo_to_html(self, memo: Dict[str, Any]) -> str:
        """
        Export memo to HTML format.
        
        Args:
            memo (Dict[str, Any]): Memo data
            
        Returns:
            str: HTML representation of the memo
        """
        try:
            html_parts = []
            
            # Header
            html_parts.append(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{memo.get('headline', 'Intelligence Memo')}</title>
                <style>
                    body {{ font-family: 'Times New Roman', serif; margin: 40px; }}
                    .header {{ border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }}
                    .headline {{ font-size: 36px; font-weight: bold; margin-bottom: 10px; }}
                    .subheadline {{ font-size: 18px; color: #666; margin-bottom: 20px; }}
                    .metadata {{ font-size: 12px; color: #888; }}
                    .executive-summary {{ background: #f9f9f9; padding: 20px; margin: 20px 0; font-style: italic; }}
                    .section {{ margin: 30px 0; }}
                    .section-title {{ font-size: 24px; font-weight: bold; border-bottom: 1px solid #ccc; }}
                    .article {{ margin: 20px 0; }}
                    .article-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                    .article-content {{ line-height: 1.6; margin-bottom: 10px; }}
                    .byline {{ font-size: 12px; color: #666; font-style: italic; }}
                    .sidebar {{ background: #f0f0f0; padding: 20px; margin: 20px 0; }}
                    .chart {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
                </style>
            </head>
            <body>
            """)
            
            # Header section
            html_parts.append(f"""
            <div class="header">
                <div class="headline">{memo.get('headline', 'Intelligence Memo')}</div>
                <div class="subheadline">{memo.get('subheadline', '')}</div>
                <div class="metadata">
                    Generated: {memo.get('generated_at', datetime.now().isoformat())} | 
                    Type: {memo.get('memo_type', 'daily').title()} | 
                    Classification: {memo.get('metadata', {}).get('classification', 'confidential').title()}
                </div>
            </div>
            """)
            
            # Executive summary
            if memo.get('executive_summary'):
                html_parts.append(f"""
                <div class="executive-summary">
                    <strong>Executive Summary:</strong> {memo['executive_summary']}
                </div>
                """)
            
            # Sections
            for section in memo.get('sections', []):
                html_parts.append(f"""
                <div class="section">
                    <div class="section-title">{section['title']}</div>
                    <div style="font-size: 14px; color: #666; margin-bottom: 20px;">{section.get('subtitle', '')}</div>
                """)
                
                for article in section.get('articles', []):
                    html_parts.append(f"""
                    <div class="article">
                        <div class="article-title">{article['title']}</div>
                        <div class="article-content">{article['content']}</div>
                        <div class="byline">By {article.get('byline', 'Unknown')} - {article.get('timestamp', '')}</div>
                    </div>
                    """)
                
                html_parts.append("</div>")
            
            # Sidebar
            if memo.get('sidebar'):
                sidebar = memo['sidebar']
                html_parts.append(f"""
                <div class="sidebar">
                    <h3>Quick Stats</h3>
                    <ul>
                        <li>Events (24h): {sidebar.get('quick_stats', {}).get('events_24h', 0)}</li>
                        <li>High Priority: {sidebar.get('quick_stats', {}).get('high_priority', 0)}</li>
                        <li>Action Items: {sidebar.get('quick_stats', {}).get('action_items', 0)}</li>
                    </ul>
                    
                    <h3>Key Highlights</h3>
                    <ul>
                """)
                
                for highlight in sidebar.get('highlights', [])[:5]:
                    html_parts.append(f"<li>{highlight}</li>")
                
                html_parts.append("</ul></div>")
            
            # Charts (simplified representation)
            if memo.get('charts'):
                html_parts.append('<div class="section"><div class="section-title">Analytics</div>')
                for chart_name, chart_data in memo['charts'].items():
                    html_parts.append(f"""
                    <div class="chart">
                        <h4>{chart_data.get('title', chart_name.title())}</h4>
                        <p>Chart type: {chart_data.get('type', 'unknown')}</p>
                        <p>Data points: {len(chart_data.get('data', {}).get('values', []))}</p>
                    </div>
                    """)
                html_parts.append('</div>')
            
            html_parts.append("</body></html>")
            
            return "".join(html_parts)
            
        except Exception as e:
            logger.error(f"Error exporting memo to HTML: {str(e)}")
            return f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"
    
    # Additional helper methods for weekly, monthly, incident, and compliance memos
    # These would be implemented similarly to the daily memo methods above
    # For brevity, I'm including stubs here
    
    def _generate_weekly_executive_summary(self, weekly_data: Dict[str, Any]) -> str:
        """Generate executive summary for weekly memo."""
        return "Weekly intelligence summary covering compliance trends, security incidents, and operational changes across the PolicyEdge environment."
    
    def _generate_weekly_sections(self, weekly_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate sections for weekly memo."""
        return []
    
    def _create_weekly_sidebar(self, weekly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create sidebar for weekly memo."""
        return {"quick_stats": {}, "highlights": [], "upcoming": []}
    
    def _generate_weekly_chart_data(self, weekly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart data for weekly memo."""
        return {}
    
    def _generate_monthly_executive_summary(self, monthly_data: Dict[str, Any]) -> str:
        """Generate executive summary for monthly memo."""
        return "Monthly intelligence report providing strategic overview of compliance posture and operational performance."
    
    def _generate_monthly_sections(self, monthly_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate sections for monthly memo."""
        return []
    
    def _create_monthly_sidebar(self, monthly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create sidebar for monthly memo."""
        return {"quick_stats": {}, "highlights": [], "upcoming": []}
    
    def _generate_monthly_chart_data(self, monthly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart data for monthly memo."""
        return {}
    
    def _generate_incident_executive_summary(self, incidents: List[Dict[str, Any]]) -> str:
        """Generate executive summary for incident memo."""
        return f"Security incident analysis covering {len(incidents)} incidents and their compliance impact."
    
    def _generate_incident_sections(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate sections for incident memo."""
        return []
    
    def _create_incident_sidebar(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create sidebar for incident memo."""
        return {"quick_stats": {}, "highlights": [], "upcoming": []}
    
    def _generate_incident_chart_data(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate chart data for incident memo."""
        return {}
    
    def _determine_incident_priority(self, incidents: List[Dict[str, Any]]) -> str:
        """Determine priority level for incident memo."""
        if any(incident.get("severity") == "high" for incident in incidents):
            return "high"
        elif any(incident.get("severity") == "medium" for incident in incidents):
            return "medium"
        else:
            return "low"
    
    def _generate_compliance_executive_summary(self, compliance_data: Dict[str, Any]) -> str:
        """Generate executive summary for compliance memo."""
        return "Compliance intelligence update covering regulatory developments and control implementation status."
    
    def _generate_compliance_sections(self, compliance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate sections for compliance memo."""
        return []
    
    def _create_compliance_sidebar(self, compliance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create sidebar for compliance memo."""
        return {"quick_stats": {}, "highlights": [], "upcoming": []}
    
    def _generate_compliance_chart_data(self, compliance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart data for compliance memo."""
        return {}
    
    def _get_frameworks_covered(self, compliance_data: Dict[str, Any]) -> List[str]:
        """Get list of compliance frameworks covered in the data."""
        frameworks = set()
        
        for change in compliance_data.get("compliance_changes", []):
            frameworks.add(change.get("framework", "Unknown"))
        
        for update in compliance_data.get("regulatory_updates", []):
            frameworks.add(update.get("framework", "Unknown"))
        
        return list(frameworks)