"""
Intelligence API endpoints for PolicyEdgeAI.

Provides live intelligence feed and newspaper-style intelligence memo capabilities.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json
import os
from intelligence import IntelligenceFeedGenerator, NewspaperMemoGenerator, DataAggregator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create router
intelligence = APIRouter(
    prefix="/api/intelligence",
    tags=["intelligence"],
    responses={404: {"description": "Intelligence data not found"}}
)


# Dependency to get intelligence components
def get_feed_generator():
    return IntelligenceFeedGenerator()


def get_memo_generator():
    return NewspaperMemoGenerator()


def get_data_aggregator():
    return DataAggregator()


# Live Intelligence Feed Endpoints
@intelligence.get("/feed", summary="Get live intelligence feed")
async def get_live_intelligence_feed(
    feed_type: str = Query("comprehensive", description="Type of feed (comprehensive, compliance, security, operations)"),
    limit: int = Query(50, description="Maximum number of feed items"),
    feed_generator: IntelligenceFeedGenerator = Depends(get_feed_generator)
):
    """
    Get live intelligence feed from PolicyEdge data sources.
    
    This endpoint generates a real-time intelligence feed combining data from
    compliance scoring, asset management, contract tracking, regulatory updates,
    and security incidents.
    """
    try:
        if feed_type not in ["comprehensive", "compliance", "security", "operations"]:
            raise HTTPException(status_code=400, detail="Invalid feed type. Must be one of: comprehensive, compliance, security, operations")
        
        if limit <= 0 or limit > 1000:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")
        
        feed = feed_generator.generate_live_feed(feed_type, limit)
        
        if "error" in feed:
            raise HTTPException(status_code=500, detail=feed["error"])
        
        return feed
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting live intelligence feed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/feed/history", summary="Get feed history")
async def get_feed_history(
    feed_type: str = Query("comprehensive", description="Type of feed"),
    limit: int = Query(10, description="Maximum number of historical feeds"),
    feed_generator: IntelligenceFeedGenerator = Depends(get_feed_generator)
):
    """
    Get historical intelligence feeds.
    
    Retrieves previously generated intelligence feeds for analysis and comparison.
    """
    try:
        if feed_type not in ["comprehensive", "compliance", "security", "operations"]:
            raise HTTPException(status_code=400, detail="Invalid feed type")
        
        feeds = feed_generator.get_feed_history(feed_type, limit)
        return {"feeds": feeds}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feed history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/feed/metrics", summary="Get feed metrics")
async def get_feed_metrics(
    feed_type: str = Query("comprehensive", description="Type of feed"),
    hours_back: int = Query(24, description="Number of hours to analyze"),
    feed_generator: IntelligenceFeedGenerator = Depends(get_feed_generator)
):
    """
    Get metrics about feed activity.
    
    Provides statistical analysis of intelligence feed activity over a specified time period.
    """
    try:
        if feed_type not in ["comprehensive", "compliance", "security", "operations"]:
            raise HTTPException(status_code=400, detail="Invalid feed type")
        
        if hours_back <= 0 or hours_back > 720:  # Max 30 days
            raise HTTPException(status_code=400, detail="Hours back must be between 1 and 720")
        
        metrics = feed_generator.get_feed_metrics(feed_type, hours_back)
        
        if "error" in metrics:
            raise HTTPException(status_code=500, detail=metrics["error"])
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feed metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/feed/item/{item_id}", summary="Get feed item details")
async def get_feed_item_details(
    item_id: str,
    feed_generator: IntelligenceFeedGenerator = Depends(get_feed_generator)
):
    """
    Get detailed information about a specific feed item.
    
    Retrieves comprehensive details about a specific intelligence feed item.
    """
    try:
        item = feed_generator.get_feed_item_details(item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail=f"Feed item {item_id} not found")
        
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feed item details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Intelligence Memo Endpoints
@intelligence.get("/memo", summary="Generate intelligence memo")
async def generate_intelligence_memo(
    memo_type: str = Query("daily", description="Type of memo (daily, weekly, monthly, incident, compliance)"),
    include_charts: bool = Query(True, description="Whether to include chart data"),
    memo_generator: NewspaperMemoGenerator = Depends(get_memo_generator)
):
    """
    Generate a newspaper-style intelligence memo.
    
    Creates a formatted intelligence memo combining data from various PolicyEdge
    sources in a newspaper-style layout with headlines, articles, and analysis.
    """
    try:
        if memo_type not in ["daily", "weekly", "monthly", "incident", "compliance"]:
            raise HTTPException(status_code=400, detail="Invalid memo type. Must be one of: daily, weekly, monthly, incident, compliance")
        
        memo = memo_generator.generate_intelligence_memo(memo_type, include_charts)
        
        if "error" in memo:
            raise HTTPException(status_code=500, detail=memo["error"])
        
        return memo
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating intelligence memo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/memo/history", summary="Get memo history")
async def get_memo_history(
    memo_type: Optional[str] = Query(None, description="Type of memo (optional filter)"),
    limit: int = Query(10, description="Maximum number of historical memos"),
    memo_generator: NewspaperMemoGenerator = Depends(get_memo_generator)
):
    """
    Get historical intelligence memos.
    
    Retrieves previously generated intelligence memos for reference and analysis.
    """
    try:
        if memo_type and memo_type not in ["daily", "weekly", "monthly", "incident", "compliance"]:
            raise HTTPException(status_code=400, detail="Invalid memo type")
        
        memos = memo_generator.get_memo_history(memo_type, limit)
        return {"memos": memos}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting memo history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/memo/{memo_id}/html", summary="Export memo to HTML")
async def export_memo_to_html(
    memo_id: str,
    memo_generator: NewspaperMemoGenerator = Depends(get_memo_generator)
):
    """
    Export a specific memo to HTML format.
    
    Generates an HTML representation of the memo for viewing or printing.
    """
    try:
        # Get memo from history (simplified lookup by ID)
        memos = memo_generator.get_memo_history(None, 50)
        memo = None
        
        for m in memos:
            # Use generated_at timestamp as ID for simplicity
            if m.get("generated_at", "").replace(":", "").replace("-", "").replace(".", "") == memo_id:
                memo = m
                break
        
        if not memo:
            raise HTTPException(status_code=404, detail=f"Memo {memo_id} not found")
        
        html_content = memo_generator.export_memo_to_html(memo)
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting memo to HTML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Data Aggregation Endpoints
@intelligence.get("/data/summary", summary="Get intelligence data summary")
async def get_intelligence_summary(
    data_aggregator: DataAggregator = Depends(get_data_aggregator)
):
    """
    Get comprehensive intelligence data summary.
    
    Provides a summary of all intelligence data sources including compliance changes,
    asset updates, contract alerts, regulatory updates, and security incidents.
    """
    try:
        summary = data_aggregator.get_intelligence_summary()
        
        if "error" in summary:
            raise HTTPException(status_code=500, detail=summary["error"])
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting intelligence summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/data/compliance", summary="Get compliance changes")
async def get_compliance_changes(
    hours_back: int = Query(24, description="Number of hours to look back"),
    data_aggregator: DataAggregator = Depends(get_data_aggregator)
):
    """
    Get compliance score changes and control updates.
    
    Retrieves recent compliance changes including score improvements,
    control implementations, and risk level updates.
    """
    try:
        if hours_back <= 0 or hours_back > 720:  # Max 30 days
            raise HTTPException(status_code=400, detail="Hours back must be between 1 and 720")
        
        changes = data_aggregator.get_compliance_changes(hours_back)
        return {"changes": changes}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compliance changes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/data/assets", summary="Get asset changes")
async def get_asset_changes(
    hours_back: int = Query(24, description="Number of hours to look back"),
    data_aggregator: DataAggregator = Depends(get_data_aggregator)
):
    """
    Get asset inventory changes and updates.
    
    Retrieves recent asset changes including new assets, status changes,
    and risk level modifications.
    """
    try:
        if hours_back <= 0 or hours_back > 720:  # Max 30 days
            raise HTTPException(status_code=400, detail="Hours back must be between 1 and 720")
        
        changes = data_aggregator.get_asset_changes(hours_back)
        return {"changes": changes}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting asset changes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/data/contracts", summary="Get contract alerts")
async def get_contract_alerts(
    days_ahead: int = Query(90, description="Number of days ahead to check for expirations"),
    data_aggregator: DataAggregator = Depends(get_data_aggregator)
):
    """
    Get contract expiration alerts and renewals.
    
    Retrieves contracts that are expiring within the specified timeframe
    and require attention for renewal or replacement.
    """
    try:
        if days_ahead <= 0 or days_ahead > 365:  # Max 1 year
            raise HTTPException(status_code=400, detail="Days ahead must be between 1 and 365")
        
        alerts = data_aggregator.get_contract_alerts(days_ahead)
        return {"alerts": alerts}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contract alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/data/regulatory", summary="Get regulatory updates")
async def get_regulatory_updates(
    hours_back: int = Query(168, description="Number of hours to look back (default: 7 days)"),
    data_aggregator: DataAggregator = Depends(get_data_aggregator)
):
    """
    Get regulatory framework updates and announcements.
    
    Retrieves recent regulatory updates including new requirements,
    clarifications, and version updates for various compliance frameworks.
    """
    try:
        if hours_back <= 0 or hours_back > 8760:  # Max 1 year
            raise HTTPException(status_code=400, detail="Hours back must be between 1 and 8760")
        
        updates = data_aggregator.get_regulatory_updates(hours_back)
        return {"updates": updates}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting regulatory updates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/data/incidents", summary="Get security incidents")
async def get_security_incidents(
    hours_back: int = Query(72, description="Number of hours to look back"),
    data_aggregator: DataAggregator = Depends(get_data_aggregator)
):
    """
    Get security incidents and their compliance impact.
    
    Retrieves recent security incidents including details about affected assets,
    compliance implications, and resolution status.
    """
    try:
        if hours_back <= 0 or hours_back > 720:  # Max 30 days
            raise HTTPException(status_code=400, detail="Hours back must be between 1 and 720")
        
        incidents = data_aggregator.get_security_incidents(hours_back)
        return {"incidents": incidents}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting security incidents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@intelligence.get("/data/trends", summary="Get trend analysis")
async def get_trend_analysis(
    days_back: int = Query(30, description="Number of days to analyze trends"),
    data_aggregator: DataAggregator = Depends(get_data_aggregator)
):
    """
    Get trend analysis and insights.
    
    Provides analytical insights about compliance trends, asset patterns,
    incident frequencies, and other key metrics over time.
    """
    try:
        if days_back <= 0 or days_back > 365:  # Max 1 year
            raise HTTPException(status_code=400, detail="Days back must be between 1 and 365")
        
        trends = data_aggregator.get_trend_analysis(days_back)
        return trends
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Utility Endpoints
@intelligence.get("/health", summary="Intelligence module health check")
async def intelligence_health_check():
    """
    Health check for intelligence module.
    
    Verifies that all intelligence components are functioning properly.
    """
    try:
        # Test data aggregator
        data_aggregator = DataAggregator()
        test_summary = data_aggregator.get_intelligence_summary()
        
        # Test feed generator
        feed_generator = IntelligenceFeedGenerator()
        test_feed = feed_generator.generate_live_feed("comprehensive", 1)
        
        # Test memo generator
        memo_generator = NewspaperMemoGenerator()
        test_memo = memo_generator.generate_intelligence_memo("daily", False)
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "data_aggregator": "healthy" if "error" not in test_summary else "error",
                "feed_generator": "healthy" if "error" not in test_feed else "error",
                "memo_generator": "healthy" if "error" not in test_memo else "error"
            },
            "test_results": {
                "data_aggregator": len(test_summary.get("data", {})),
                "feed_generator": test_feed.get("total_items", 0),
                "memo_generator": len(test_memo.get("sections", []))
            }
        }
        
        # Determine overall health
        if any(status == "error" for status in health_status["components"].values()):
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Intelligence health check failed: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "components": {
                "data_aggregator": "unknown",
                "feed_generator": "unknown",
                "memo_generator": "unknown"
            }
        }