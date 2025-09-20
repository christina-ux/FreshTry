"""
Live Intelligence Feed models and data structures.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class IntelligenceSource(str, Enum):
    """Sources of intelligence data."""
    WEB_SCRAPING = "web_scraping"
    RSS_FEEDS = "rss_feeds"
    GOOGLE_DRIVE = "google_drive"
    AIPRM_CHATS = "aiprm_chats"
    REGULATORY_FEEDS = "regulatory_feeds"
    CUSTOM_AGENTS = "custom_agents"
    TRIPWIRE_ALERTS = "tripwire_alerts"
    USER_UPLOADS = "user_uploads"


class IntelligenceCategory(str, Enum):
    """Categories of intelligence information."""
    MARKET_SHOCK = "market_shock"
    REGULATORY_CHANGE = "regulatory_change"
    POLICY_SHIFT = "policy_shift"
    AI_DEVELOPMENT = "ai_development"
    VOLATILITY_ALERT = "volatility_alert"
    POLITICAL_EVENT = "political_event"
    BLACK_BOX_DISCOVERY = "black_box_discovery"
    RISK_EXPOSURE = "risk_exposure"


class TripwireStatus(str, Enum):
    """Status of tripwire alerts."""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    RESOLVED = "resolved"
    DISABLED = "disabled"


class IntelligenceItem(BaseModel):
    """Core intelligence data item."""
    id: str = Field(..., description="Unique identifier for the intelligence item")
    title: str = Field(..., description="Title or headline of the intelligence")
    content: str = Field(..., description="Full content of the intelligence")
    summary: str = Field(..., description="Executive summary")
    source: IntelligenceSource = Field(..., description="Source of the intelligence")
    category: IntelligenceCategory = Field(..., description="Category of intelligence")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    impact_score: float = Field(..., ge=0, le=10, description="Impact score (0-10)")
    urgency_score: float = Field(..., ge=0, le=10, description="Urgency score (0-10)")
    risk_score: float = Field(..., ge=0, le=10, description="Risk score (0-10)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    related_entities: List[str] = Field(default_factory=list, description="Related entities/companies")
    source_url: Optional[str] = Field(None, description="Original source URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TripwireRule(BaseModel):
    """Tripwire rule definition."""
    id: str = Field(..., description="Unique identifier for the tripwire")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Description of what triggers this rule")
    pattern: str = Field(..., description="Pattern or keyword to match")
    category: IntelligenceCategory = Field(..., description="Category this tripwire monitors")
    threshold: float = Field(..., description="Threshold for triggering")
    status: TripwireStatus = Field(default=TripwireStatus.ACTIVE)
    last_triggered: Optional[datetime] = Field(None)
    trigger_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LiveFeed(BaseModel):
    """Live intelligence feed."""
    id: str = Field(..., description="Unique identifier for the feed")
    name: str = Field(..., description="Feed name")
    description: str = Field(..., description="Feed description")
    items: List[IntelligenceItem] = Field(default_factory=list)
    categories: List[IntelligenceCategory] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    subscriber_count: int = Field(default=0)
    is_premium: bool = Field(default=False)


class IntelligenceMemo(BaseModel):
    """Professional intelligence memo."""
    id: str = Field(..., description="Unique identifier for the memo")
    title: str = Field(..., description="Memo title")
    executive_summary: str = Field(..., description="Executive summary")
    key_insights: List[str] = Field(..., description="Key insights")
    risk_assessment: str = Field(..., description="Risk assessment section")
    recommendations: List[str] = Field(..., description="Action recommendations")
    market_analysis: Optional[str] = Field(None, description="Market analysis section")
    regulatory_updates: Optional[str] = Field(None, description="Regulatory updates section")
    ai_intelligence: Optional[str] = Field(None, description="AI intelligence section")
    sources: List[IntelligenceItem] = Field(..., description="Source intelligence items")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    memo_type: str = Field(default="daily", description="Type of memo (daily, weekly, alert)")
    target_audience: str = Field(default="executive", description="Target audience")
    classification: str = Field(default="internal", description="Classification level")


class UserAction(BaseModel):
    """User action tracking for self-evolving intelligence."""
    id: str = Field(..., description="Unique identifier for the action")
    user_id: str = Field(..., description="User identifier")
    action_type: str = Field(..., description="Type of action (click, read, share, bookmark)")
    target_id: str = Field(..., description="ID of the target item (memo, feed item, etc.)")
    target_type: str = Field(..., description="Type of target (memo, intelligence_item, feed)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = Field(None, description="Session identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional action metadata")


class LearningDelta(BaseModel):
    """Learning delta for self-evolving system."""
    id: str = Field(..., description="Unique identifier for the delta")
    change_type: str = Field(..., description="Type of change (tripwire_update, pattern_learn, preference_update)")
    description: str = Field(..., description="Description of the change")
    before_state: Dict[str, Any] = Field(..., description="State before change")
    after_state: Dict[str, Any] = Field(..., description="State after change")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the change")
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    source_actions: List[str] = Field(..., description="User action IDs that led to this change")


class MonetizationTier(str, Enum):
    """Monetization tiers."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class Subscription(BaseModel):
    """User subscription model."""
    id: str = Field(..., description="Unique identifier for the subscription")
    user_id: str = Field(..., description="User identifier")
    tier: MonetizationTier = Field(..., description="Subscription tier")
    feeds: List[str] = Field(..., description="Subscribed feed IDs")
    categories: List[IntelligenceCategory] = Field(..., description="Subscribed categories")
    max_memos_per_day: int = Field(..., description="Maximum memos per day")
    max_feeds: int = Field(..., description="Maximum feeds")
    has_api_access: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None)
    is_active: bool = Field(default=True)