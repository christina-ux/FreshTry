"""
Data ingestion layer for Live Intelligence Feed system.
Handles multiple data sources including web scraping, RSS feeds, Google Drive, etc.
"""
import asyncio
import logging
import re
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .models import IntelligenceItem, IntelligenceSource, IntelligenceCategory, TripwireRule

logger = logging.getLogger(__name__)


@dataclass
class SourceConfig:
    """Configuration for a data source."""
    name: str
    source_type: IntelligenceSource
    endpoint: str
    headers: Dict[str, str] = None
    auth_token: str = None
    polling_interval: int = 300  # seconds
    enabled: bool = True
    categories: List[IntelligenceCategory] = None


class DataSourceBase(ABC):
    """Base class for data sources."""
    
    def __init__(self, config: SourceConfig):
        self.config = config
        self.last_poll = None
        
    @abstractmethod
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch raw data from the source."""
        pass
    
    @abstractmethod
    def parse_item(self, raw_item: Dict[str, Any]) -> Optional[IntelligenceItem]:
        """Parse raw item into IntelligenceItem."""
        pass
    
    async def collect_intelligence(self) -> List[IntelligenceItem]:
        """Collect and parse intelligence from this source."""
        try:
            raw_data = await self.fetch_data()
            items = []
            
            for raw_item in raw_data:
                try:
                    item = self.parse_item(raw_item)
                    if item:
                        items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing item from {self.config.name}: {e}")
                    
            self.last_poll = datetime.utcnow()
            logger.info(f"Collected {len(items)} items from {self.config.name}")
            return items
            
        except Exception as e:
            logger.error(f"Error collecting from {self.config.name}: {e}")
            return []


class RSSFeedSource(DataSourceBase):
    """RSS feed data source."""
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch RSS feed data."""
        try:
            # Run feedparser in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, self.config.endpoint)
            
            if feed.bozo:
                logger.warning(f"RSS feed {self.config.name} has parsing issues: {feed.bozo_exception}")
            
            return feed.entries
        except Exception as e:
            logger.error(f"Error fetching RSS feed {self.config.name}: {e}")
            return []
    
    def parse_item(self, raw_item: Dict[str, Any]) -> Optional[IntelligenceItem]:
        """Parse RSS feed entry."""
        try:
            # Extract basic information
            title = raw_item.get('title', '').strip()
            content = raw_item.get('description', '') or raw_item.get('summary', '')
            link = raw_item.get('link', '')
            
            if not title or not content:
                return None
            
            # Parse publication date
            pub_date = raw_item.get('published_parsed')
            if pub_date:
                timestamp = datetime(*pub_date[:6])
            else:
                timestamp = datetime.utcnow()
            
            # Determine category based on content analysis
            category = self._categorize_content(title + " " + content)
            
            # Calculate basic scores (would be enhanced with ML)
            confidence_score = 0.7  # Base confidence for RSS feeds
            impact_score = self._calculate_impact_score(title, content)
            urgency_score = self._calculate_urgency_score(title, content, timestamp)
            risk_score = self._calculate_risk_score(title, content)
            
            # Extract tags
            tags = self._extract_tags(title, content)
            
            return IntelligenceItem(
                id=f"rss_{hash(link)}_{int(timestamp.timestamp())}",
                title=title,
                content=content,
                summary=content[:200] + "..." if len(content) > 200 else content,
                source=IntelligenceSource.RSS_FEEDS,
                category=category,
                confidence_score=confidence_score,
                impact_score=impact_score,
                urgency_score=urgency_score,
                risk_score=risk_score,
                timestamp=timestamp,
                tags=tags,
                source_url=link,
                metadata={
                    'feed_name': self.config.name,
                    'author': raw_item.get('author', ''),
                    'published': raw_item.get('published', '')
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing RSS item: {e}")
            return None
    
    def _categorize_content(self, text: str) -> IntelligenceCategory:
        """Categorize content based on keywords."""
        text_lower = text.lower()
        
        # Market/financial keywords
        if any(word in text_lower for word in ['market', 'stock', 'trading', 'financial', 'economic', 'volatility']):
            return IntelligenceCategory.MARKET_SHOCK
            
        # Regulatory keywords
        if any(word in text_lower for word in ['regulation', 'compliance', 'law', 'policy', 'rule', 'mandate']):
            return IntelligenceCategory.REGULATORY_CHANGE
            
        # AI keywords
        if any(word in text_lower for word in ['artificial intelligence', 'ai', 'machine learning', 'ml', 'neural', 'gpt']):
            return IntelligenceCategory.AI_DEVELOPMENT
            
        # Political keywords
        if any(word in text_lower for word in ['election', 'government', 'political', 'congress', 'senate', 'president']):
            return IntelligenceCategory.POLITICAL_EVENT
            
        # Default to policy shift
        return IntelligenceCategory.POLICY_SHIFT
    
    def _calculate_impact_score(self, title: str, content: str) -> float:
        """Calculate impact score based on content."""
        text = (title + " " + content).lower()
        
        # High impact keywords
        high_impact_words = ['crisis', 'emergency', 'major', 'significant', 'unprecedented', 'breakthrough']
        impact_score = 3.0  # Base score
        
        for word in high_impact_words:
            if word in text:
                impact_score += 1.5
                
        # Cap at 10
        return min(impact_score, 10.0)
    
    def _calculate_urgency_score(self, title: str, content: str, timestamp: datetime) -> float:
        """Calculate urgency score."""
        # Recent items are more urgent
        time_diff = datetime.utcnow() - timestamp
        urgency_score = max(5.0 - (time_diff.days * 0.5), 1.0)
        
        # Urgent keywords
        text = (title + " " + content).lower()
        urgent_words = ['urgent', 'immediate', 'breaking', 'alert', 'now', 'today']
        
        for word in urgent_words:
            if word in text:
                urgency_score += 2.0
                
        return min(urgency_score, 10.0)
    
    def _calculate_risk_score(self, title: str, content: str) -> float:
        """Calculate risk score."""
        text = (title + " " + content).lower()
        
        risk_words = ['risk', 'threat', 'danger', 'warning', 'concern', 'problem', 'issue']
        risk_score = 2.0  # Base score
        
        for word in risk_words:
            if word in text:
                risk_score += 1.0
                
        return min(risk_score, 10.0)
    
    def _extract_tags(self, title: str, content: str) -> List[str]:
        """Extract tags from content."""
        text = title + " " + content
        
        # Simple tag extraction (would be enhanced with NLP)
        tags = []
        
        # Company names (simplified)
        companies = re.findall(r'\b[A-Z][a-z]*\s+(?:Inc|Corp|Ltd|LLC|Company)\b', text)
        tags.extend([company.strip() for company in companies])
        
        # Hashtags
        hashtags = re.findall(r'#\w+', text)
        tags.extend([tag[1:] for tag in hashtags])
        
        # Common entities
        entities = re.findall(r'\b[A-Z]{2,}\b', text)  # All caps words
        tags.extend([entity for entity in entities if len(entity) > 2])
        
        return list(set(tags))[:10]  # Limit to 10 unique tags


class WebScrapingSource(DataSourceBase):
    """Web scraping data source."""
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data by scraping web pages."""
        try:
            headers = self.config.headers or {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.config.endpoint, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Simple HTML parsing (would be enhanced with BeautifulSoup)
            content = response.text
            
            # Extract basic information (this is a simplified example)
            return [{
                'title': 'Web Scraped Content',
                'content': content[:1000],  # First 1000 chars
                'url': self.config.endpoint,
                'timestamp': datetime.utcnow()
            }]
            
        except Exception as e:
            logger.error(f"Error scraping {self.config.name}: {e}")
            return []
    
    def parse_item(self, raw_item: Dict[str, Any]) -> Optional[IntelligenceItem]:
        """Parse scraped content."""
        try:
            return IntelligenceItem(
                id=f"web_{hash(raw_item['url'])}_{int(raw_item['timestamp'].timestamp())}",
                title=raw_item['title'],
                content=raw_item['content'],
                summary=raw_item['content'][:200] + "...",
                source=IntelligenceSource.WEB_SCRAPING,
                category=IntelligenceCategory.POLICY_SHIFT,
                confidence_score=0.6,
                impact_score=5.0,
                urgency_score=3.0,
                risk_score=3.0,
                timestamp=raw_item['timestamp'],
                source_url=raw_item['url'],
                metadata={'scraping_source': self.config.name}
            )
        except Exception as e:
            logger.error(f"Error parsing web scraped item: {e}")
            return None


class TripwireMonitor:
    """Monitor for tripwire alerts."""
    
    def __init__(self, rules: List[TripwireRule]):
        self.rules = {rule.id: rule for rule in rules}
        
    def check_tripwires(self, items: List[IntelligenceItem]) -> List[IntelligenceItem]:
        """Check items against tripwire rules."""
        triggered_items = []
        
        for item in items:
            for rule in self.rules.values():
                if self._matches_rule(item, rule):
                    # Create tripwire alert
                    alert_item = self._create_alert_item(item, rule)
                    triggered_items.append(alert_item)
                    
                    # Update rule
                    rule.last_triggered = datetime.utcnow()
                    rule.trigger_count += 1
                    
        return triggered_items
    
    def _matches_rule(self, item: IntelligenceItem, rule: TripwireRule) -> bool:
        """Check if item matches tripwire rule."""
        if rule.status != "active":
            return False
            
        # Category match
        if item.category != rule.category:
            return False
            
        # Pattern match (simple keyword search)
        text = (item.title + " " + item.content).lower()
        if rule.pattern.lower() not in text:
            return False
            
        # Threshold check (using impact score)
        if item.impact_score < rule.threshold:
            return False
            
        return True
    
    def _create_alert_item(self, item: IntelligenceItem, rule: TripwireRule) -> IntelligenceItem:
        """Create alert item from triggered tripwire."""
        return IntelligenceItem(
            id=f"tripwire_{rule.id}_{item.id}",
            title=f"TRIPWIRE ALERT: {rule.name}",
            content=f"Tripwire '{rule.name}' triggered by: {item.title}\n\nOriginal content:\n{item.content}",
            summary=f"Tripwire alert for {rule.name}",
            source=IntelligenceSource.TRIPWIRE_ALERTS,
            category=rule.category,
            confidence_score=0.9,
            impact_score=min(item.impact_score * 1.5, 10.0),
            urgency_score=min(item.urgency_score * 1.3, 10.0),
            risk_score=min(item.risk_score * 1.5, 10.0),
            timestamp=datetime.utcnow(),
            tags=item.tags + [f"tripwire_{rule.id}"],
            source_url=item.source_url,
            metadata={
                'tripwire_id': rule.id,
                'tripwire_name': rule.name,
                'original_item_id': item.id,
                'trigger_count': rule.trigger_count
            }
        )


class IntelligenceCollector:
    """Main intelligence collection orchestrator."""
    
    def __init__(self):
        self.sources: List[DataSourceBase] = []
        self.tripwire_monitor = None
        
    def add_source(self, source: DataSourceBase):
        """Add a data source."""
        self.sources.append(source)
        
    def set_tripwire_monitor(self, monitor: TripwireMonitor):
        """Set tripwire monitor."""
        self.tripwire_monitor = monitor
        
    async def collect_all(self) -> List[IntelligenceItem]:
        """Collect from all sources."""
        all_items = []
        
        # Collect from all sources concurrently
        tasks = [source.collect_intelligence() for source in self.sources if source.config.enabled]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
            else:
                logger.error(f"Collection error: {result}")
        
        # Check tripwires if monitor is set
        if self.tripwire_monitor:
            tripwire_alerts = self.tripwire_monitor.check_tripwires(all_items)
            all_items.extend(tripwire_alerts)
        
        # Sort by urgency and impact
        all_items.sort(key=lambda x: (x.urgency_score + x.impact_score), reverse=True)
        
        logger.info(f"Collected {len(all_items)} total intelligence items")
        return all_items


def create_default_sources() -> List[SourceConfig]:
    """Create default source configurations."""
    return [
        SourceConfig(
            name="Reuters Business",
            source_type=IntelligenceSource.RSS_FEEDS,
            endpoint="https://feeds.reuters.com/reuters/businessNews",
            categories=[IntelligenceCategory.MARKET_SHOCK, IntelligenceCategory.POLICY_SHIFT]
        ),
        SourceConfig(
            name="SEC Regulatory Feeds",
            source_type=IntelligenceSource.RSS_FEEDS,
            endpoint="https://www.sec.gov/news/pressreleases.rss",
            categories=[IntelligenceCategory.REGULATORY_CHANGE]
        ),
        SourceConfig(
            name="AI News",
            source_type=IntelligenceSource.RSS_FEEDS,
            endpoint="https://feeds.feedburner.com/oreilly/radar",
            categories=[IntelligenceCategory.AI_DEVELOPMENT]
        ),
        SourceConfig(
            name="Financial Times",
            source_type=IntelligenceSource.RSS_FEEDS,
            endpoint="https://www.ft.com/rss/home/us",
            categories=[IntelligenceCategory.MARKET_SHOCK, IntelligenceCategory.POLITICAL_EVENT]
        )
    ]


def create_default_tripwires() -> List[TripwireRule]:
    """Create default tripwire rules."""
    return [
        TripwireRule(
            id="market_crash_alert",
            name="Market Crash Alert",
            description="Triggers on major market movements",
            pattern="crash|plunge|collapse|fall|drop",
            category=IntelligenceCategory.MARKET_SHOCK,
            threshold=7.0
        ),
        TripwireRule(
            id="ai_breakthrough",
            name="AI Breakthrough",
            description="Triggers on significant AI developments",
            pattern="breakthrough|advancement|revolutionary|artificial intelligence",
            category=IntelligenceCategory.AI_DEVELOPMENT,
            threshold=6.0
        ),
        TripwireRule(
            id="regulatory_emergency",
            name="Regulatory Emergency",
            description="Triggers on urgent regulatory changes",
            pattern="emergency|urgent|immediate|regulation|compliance",
            category=IntelligenceCategory.REGULATORY_CHANGE,
            threshold=8.0
        )
    ]