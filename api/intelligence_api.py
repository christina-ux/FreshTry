"""
API endpoints for Live Intelligence Feed system.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field

from intelligence.models import (
    IntelligenceItem, IntelligenceMemo, LiveFeed, TripwireRule,
    UserAction, LearningDelta, IntelligenceCategory, IntelligenceSource,
    MonetizationTier, Subscription
)
from intelligence.ingestion import (
    IntelligenceCollector, RSSFeedSource, WebScrapingSource, TripwireMonitor,
    create_default_sources, create_default_tripwires, SourceConfig
)
from intelligence.memo_generator import MemoGenerator, FeedManager, create_default_feeds
from intelligence.self_evolving import ActionTracker, LearningEngine, ContinuousLearningOrchestrator

logger = logging.getLogger(__name__)

# Global instances (in production these would be dependency injected)
intelligence_collector = IntelligenceCollector()
memo_generator = MemoGenerator()
feed_manager = FeedManager()
action_tracker = ActionTracker()
learning_engine = LearningEngine(action_tracker)
learning_orchestrator = ContinuousLearningOrchestrator(learning_engine)

# System initialization flag
_system_initialized = False

# Initialize default components
def initialize_intelligence_system():
    """Initialize the intelligence system with default configurations."""
    global intelligence_collector, feed_manager, _system_initialized
    
    if _system_initialized:
        return
    
    # Add default sources
    default_sources = create_default_sources()
    for source_config in default_sources:
        if source_config.source_type == IntelligenceSource.RSS_FEEDS:
            source = RSSFeedSource(source_config)
            intelligence_collector.add_source(source)
        elif source_config.source_type == IntelligenceSource.WEB_SCRAPING:
            source = WebScrapingSource(source_config)
            intelligence_collector.add_source(source)
    
    # Setup tripwire monitor
    default_tripwires = create_default_tripwires()
    tripwire_monitor = TripwireMonitor(default_tripwires)
    intelligence_collector.set_tripwire_monitor(tripwire_monitor)
    
    # Create default feeds
    create_default_feeds(feed_manager)
    
    _system_initialized = True
    logger.info("Intelligence system initialized with default configurations")

router = APIRouter(prefix="/api/intelligence", tags=["Live Intelligence Feed"])


# Request/Response Models
class CollectionRequest(BaseModel):
    """Request to trigger intelligence collection."""
    sources: Optional[List[str]] = Field(None, description="Specific sources to collect from")
    categories: Optional[List[IntelligenceCategory]] = Field(None, description="Filter by categories")


class MemoRequest(BaseModel):
    """Request to generate intelligence memo."""
    memo_type: str = Field("daily", description="Type of memo (daily, weekly, alert)")
    target_audience: str = Field("executive", description="Target audience")
    hours_back: int = Field(24, description="Hours of data to include")
    min_impact_score: float = Field(3.0, description="Minimum impact score for inclusion")
    categories: Optional[List[IntelligenceCategory]] = Field(None, description="Categories to include")


class FeedRequest(BaseModel):
    """Request to create new feed."""
    name: str = Field(..., description="Feed name")
    description: str = Field(..., description="Feed description")
    categories: List[IntelligenceCategory] = Field(..., description="Categories to include")
    is_premium: bool = Field(False, description="Whether this is a premium feed")


class UserActionRequest(BaseModel):
    """Request to track user action."""
    user_id: str = Field(..., description="User identifier")
    action_type: str = Field(..., description="Type of action")
    target_id: str = Field(..., description="Target item ID")
    target_type: str = Field(..., description="Target type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TripwireRequest(BaseModel):
    """Request to create tripwire rule."""
    name: str = Field(..., description="Tripwire name")
    description: str = Field(..., description="Description")
    pattern: str = Field(..., description="Pattern to match")
    category: IntelligenceCategory = Field(..., description="Category to monitor")
    threshold: float = Field(..., description="Threshold for triggering")


# Intelligence Collection Endpoints
@router.post("/collect", response_model=Dict[str, Any])
async def trigger_collection(
    request: CollectionRequest,
    background_tasks: BackgroundTasks
):
    """Trigger intelligence collection from all or specified sources."""
    try:
        # Initialize system if not already done
        initialize_intelligence_system()
        
        # Run collection in background
        background_tasks.add_task(run_collection_cycle)
        
        return {
            "status": "success",
            "message": "Intelligence collection initiated",
            "timestamp": datetime.utcnow(),
            "sources": len(intelligence_collector.sources)
        }
    except Exception as e:
        logger.error(f"Error triggering collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_collection_cycle():
    """Run a complete collection cycle."""
    try:
        # Collect intelligence
        items = await intelligence_collector.collect_all()
        
        # Update all feeds
        for feed in feed_manager.list_feeds():
            feed_manager.update_feed(feed.id, items)
        
        logger.info(f"Collection cycle completed: {len(items)} items collected")
    except Exception as e:
        logger.error(f"Error in collection cycle: {e}")


@router.get("/items", response_model=List[IntelligenceItem])
async def get_intelligence_items(
    hours_back: int = Query(24, description="Hours back to retrieve"),
    category: Optional[IntelligenceCategory] = Query(None, description="Filter by category"),
    min_impact: float = Query(0.0, description="Minimum impact score"),
    limit: int = Query(50, description="Maximum number of items")
):
    """Get recent intelligence items."""
    try:
        # Get items from all feeds
        all_items = []
        for feed in feed_manager.list_feeds():
            items = feed_manager.get_filtered_items(
                feed.id, 
                hours_back=hours_back,
                min_impact=min_impact,
                categories=[category] if category else None
            )
            all_items.extend(items)
        
        # Remove duplicates and sort
        unique_items = {item.id: item for item in all_items}.values()
        sorted_items = sorted(
            unique_items, 
            key=lambda x: x.impact_score + x.urgency_score, 
            reverse=True
        )
        
        return sorted_items[:limit]
    except Exception as e:
        logger.error(f"Error retrieving intelligence items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Memo Generation Endpoints
@router.post("/memo/generate", response_model=IntelligenceMemo)
async def generate_memo(request: MemoRequest):
    """Generate intelligence memo."""
    try:
        # Get recent items
        cutoff_time = datetime.utcnow() - timedelta(hours=request.hours_back)
        
        all_items = []
        for feed in feed_manager.list_feeds():
            items = [
                item for item in feed.items
                if (item.timestamp >= cutoff_time and
                    item.impact_score >= request.min_impact_score and
                    (not request.categories or item.category in request.categories))
            ]
            all_items.extend(items)
        
        # Remove duplicates
        unique_items = list({item.id: item for item in all_items}.values())
        
        if not unique_items:
            raise HTTPException(status_code=404, detail="No intelligence items found for memo generation")
        
        # Generate memo
        memo = memo_generator.generate_memo(
            unique_items,
            memo_type=request.memo_type,
            target_audience=request.target_audience
        )
        
        return memo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating memo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memo/{memo_id}", response_model=IntelligenceMemo)
async def get_memo(memo_id: str):
    """Get specific memo by ID."""
    # In production, this would retrieve from database
    raise HTTPException(status_code=501, detail="Memo storage not implemented")


# Feed Management Endpoints
@router.post("/feed/create", response_model=LiveFeed)
async def create_feed(request: FeedRequest):
    """Create new intelligence feed."""
    try:
        feed = feed_manager.create_feed(
            name=request.name,
            description=request.description,
            categories=request.categories,
            is_premium=request.is_premium
        )
        return feed
    except Exception as e:
        logger.error(f"Error creating feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feeds", response_model=List[LiveFeed])
async def list_feeds(include_premium: bool = Query(True, description="Include premium feeds")):
    """List all available feeds."""
    try:
        feeds = feed_manager.list_feeds(include_premium=include_premium)
        return feeds
    except Exception as e:
        logger.error(f"Error listing feeds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed/{feed_id}", response_model=LiveFeed)
async def get_feed(feed_id: str):
    """Get specific feed."""
    try:
        feed = feed_manager.get_feed(feed_id)
        if not feed:
            raise HTTPException(status_code=404, detail="Feed not found")
        return feed
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed/{feed_id}/items", response_model=List[IntelligenceItem])
async def get_feed_items(
    feed_id: str,
    hours_back: int = Query(24, description="Hours back to retrieve"),
    min_impact: float = Query(0.0, description="Minimum impact score"),
    limit: int = Query(50, description="Maximum number of items")
):
    """Get items from specific feed."""
    try:
        items = feed_manager.get_filtered_items(
            feed_id, 
            hours_back=hours_back,
            min_impact=min_impact
        )
        
        if not items:
            raise HTTPException(status_code=404, detail="No items found for this feed")
        
        return items[:limit]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving feed items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# User Action Tracking Endpoints
@router.post("/action/track", response_model=UserAction)
async def track_action(request: UserActionRequest):
    """Track user action for learning."""
    try:
        action = action_tracker.track_action(
            user_id=request.user_id,
            action_type=request.action_type,
            target_id=request.target_id,
            target_type=request.target_type,
            metadata=request.metadata
        )
        return action
    except Exception as e:
        logger.error(f"Error tracking action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/preferences", response_model=Dict[str, Any])
async def get_user_preferences(user_id: str):
    """Get learned user preferences."""
    try:
        preferences = action_tracker.get_user_preferences(user_id)
        return preferences
    except Exception as e:
        logger.error(f"Error retrieving user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/personalized", response_model=List[IntelligenceItem])
async def get_personalized_feed(
    user_id: str,
    hours_back: int = Query(24, description="Hours back to retrieve"),
    limit: int = Query(20, description="Maximum number of items")
):
    """Get personalized intelligence feed for user."""
    try:
        # Get all recent items
        all_items = []
        for feed in feed_manager.list_feeds():
            items = feed_manager.get_filtered_items(feed.id, hours_back=hours_back)
            all_items.extend(items)
        
        # Remove duplicates
        unique_items = list({item.id: item for item in all_items}.values())
        
        # Apply personalized scoring
        scored_items = []
        for item in unique_items:
            personalized_score = learning_engine.get_personalized_scoring(user_id, item)
            scored_items.append((personalized_score, item))
        
        # Sort by personalized score
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        return [item for score, item in scored_items[:limit]]
    except Exception as e:
        logger.error(f"Error generating personalized feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Tripwire Management Endpoints
@router.post("/tripwire/create", response_model=TripwireRule)
async def create_tripwire(request: TripwireRequest):
    """Create new tripwire rule."""
    try:
        tripwire = TripwireRule(
            id=f"tripwire_{request.name.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}",
            name=request.name,
            description=request.description,
            pattern=request.pattern,
            category=request.category,
            threshold=request.threshold
        )
        
        # Add to monitor
        if intelligence_collector.tripwire_monitor:
            intelligence_collector.tripwire_monitor.rules[tripwire.id] = tripwire
        
        return tripwire
    except Exception as e:
        logger.error(f"Error creating tripwire: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tripwires", response_model=List[TripwireRule])
async def list_tripwires():
    """List all tripwire rules."""
    try:
        if not intelligence_collector.tripwire_monitor:
            return []
        
        return list(intelligence_collector.tripwire_monitor.rules.values())
    except Exception as e:
        logger.error(f"Error listing tripwires: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Learning System Endpoints
@router.post("/learning/cycle", response_model=Dict[str, Any])
async def trigger_learning_cycle():
    """Trigger learning cycle manually."""
    try:
        results = await learning_orchestrator.run_learning_cycle()
        return results
    except Exception as e:
        logger.error(f"Error in learning cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/health", response_model=Dict[str, Any])
async def get_learning_health():
    """Get learning system health metrics."""
    try:
        health = learning_engine.get_system_health_metrics()
        health['learning_orchestrator'] = {
            'last_cycle': learning_orchestrator.last_learning_cycle,
            'interval_hours': learning_orchestrator.interval_hours,
            'should_run_cycle': learning_orchestrator.should_run_cycle()
        }
        return health
    except Exception as e:
        logger.error(f"Error retrieving learning health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/deltas", response_model=List[LearningDelta])
async def get_learning_deltas(
    hours_back: int = Query(24, description="Hours back to retrieve"),
    limit: int = Query(50, description="Maximum number of deltas")
):
    """Get recent learning deltas."""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        recent_deltas = [
            delta for delta in learning_engine.learning_deltas
            if delta.applied_at >= cutoff_time
        ]
        
        # Sort by application time (newest first)
        recent_deltas.sort(key=lambda x: x.applied_at, reverse=True)
        
        return recent_deltas[:limit]
    except Exception as e:
        logger.error(f"Error retrieving learning deltas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System Status Endpoints
@router.get("/status", response_model=Dict[str, Any])
async def get_system_status():
    """Get overall system status."""
    try:
        return {
            "timestamp": datetime.utcnow(),
            "sources": {
                "total": len(intelligence_collector.sources),
                "enabled": len([s for s in intelligence_collector.sources if s.config.enabled])
            },
            "feeds": {
                "total": len(feed_manager.feeds),
                "premium": len([f for f in feed_manager.feeds.values() if f.is_premium])
            },
            "tripwires": {
                "total": len(intelligence_collector.tripwire_monitor.rules) if intelligence_collector.tripwire_monitor else 0,
                "active": len([r for r in intelligence_collector.tripwire_monitor.rules.values() if r.status == "active"]) if intelligence_collector.tripwire_monitor else 0
            },
            "learning": {
                "total_actions": len(action_tracker.actions),
                "total_deltas": len(learning_engine.learning_deltas),
                "unique_users": len(set(action.user_id for action in action_tracker.actions))
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Background tasks for continuous operation
async def continuous_collection_task():
    """Background task for continuous intelligence collection."""
    while True:
        try:
            await run_collection_cycle()
            
            # Run learning cycle if due
            if learning_orchestrator.should_run_cycle():
                await learning_orchestrator.run_learning_cycle()
            
            # Wait before next cycle (e.g., 15 minutes)
            await asyncio.sleep(900)
            
        except Exception as e:
            logger.error(f"Error in continuous collection task: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error


# Initialize background task on app startup
@router.on_event("startup")
async def startup_event():
    """Initialize intelligence system on startup."""
    initialize_intelligence_system()
    # Start background collection task
    asyncio.create_task(continuous_collection_task())