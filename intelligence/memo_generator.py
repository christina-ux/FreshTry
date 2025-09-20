"""
Memo generation and feed creation for Live Intelligence Feed system.
Provides WSJ/McKinsey-style professional intelligence memos.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
from .models import (
    IntelligenceItem, IntelligenceMemo, LiveFeed, IntelligenceCategory,
    IntelligenceSource, MonetizationTier
)

logger = logging.getLogger(__name__)


class MemoGenerator:
    """Generates professional intelligence memos."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        
    def generate_memo(self, 
                     items: List[IntelligenceItem], 
                     memo_type: str = "daily",
                     target_audience: str = "executive") -> IntelligenceMemo:
        """Generate a professional intelligence memo."""
        
        # Sort items by importance
        sorted_items = sorted(items, key=lambda x: x.impact_score + x.urgency_score, reverse=True)
        
        # Group by category
        categorized = self._categorize_items(sorted_items)
        
        # Generate memo components
        title = self._generate_title(memo_type, sorted_items)
        executive_summary = self._generate_executive_summary(sorted_items[:5])
        key_insights = self._generate_key_insights(sorted_items)
        risk_assessment = self._generate_risk_assessment(sorted_items)
        recommendations = self._generate_recommendations(sorted_items)
        
        # Generate specialized sections
        market_analysis = self._generate_market_analysis(categorized.get(IntelligenceCategory.MARKET_SHOCK, []))
        regulatory_updates = self._generate_regulatory_updates(categorized.get(IntelligenceCategory.REGULATORY_CHANGE, []))
        ai_intelligence = self._generate_ai_intelligence(categorized.get(IntelligenceCategory.AI_DEVELOPMENT, []))
        
        memo_id = f"memo_{memo_type}_{int(datetime.utcnow().timestamp())}"
        
        return IntelligenceMemo(
            id=memo_id,
            title=title,
            executive_summary=executive_summary,
            key_insights=key_insights,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            market_analysis=market_analysis,
            regulatory_updates=regulatory_updates,
            ai_intelligence=ai_intelligence,
            sources=sorted_items,
            memo_type=memo_type,
            target_audience=target_audience
        )
    
    def _categorize_items(self, items: List[IntelligenceItem]) -> Dict[IntelligenceCategory, List[IntelligenceItem]]:
        """Group items by category."""
        categorized = {}
        for item in items:
            if item.category not in categorized:
                categorized[item.category] = []
            categorized[item.category].append(item)
        return categorized
    
    def _generate_title(self, memo_type: str, items: List[IntelligenceItem]) -> str:
        """Generate memo title."""
        date_str = datetime.utcnow().strftime("%B %d, %Y")
        
        if memo_type == "daily":
            return f"Daily Intelligence Brief - {date_str}"
        elif memo_type == "weekly":
            return f"Weekly Intelligence Summary - {date_str}"
        elif memo_type == "alert":
            if items:
                top_item = items[0]
                return f"INTELLIGENCE ALERT: {top_item.title[:50]}... - {date_str}"
            return f"Intelligence Alert - {date_str}"
        else:
            return f"Intelligence Memo - {date_str}"
    
    def _generate_executive_summary(self, top_items: List[IntelligenceItem]) -> str:
        """Generate executive summary."""
        if not top_items:
            return "No significant intelligence to report at this time."
        
        summary_parts = [
            "**EXECUTIVE SUMMARY**",
            "",
            f"This briefing covers {len(top_items)} priority intelligence items requiring executive attention:",
            ""
        ]
        
        for i, item in enumerate(top_items[:3], 1):
            impact_level = "HIGH" if item.impact_score >= 7 else "MEDIUM" if item.impact_score >= 4 else "LOW"
            summary_parts.append(f"{i}. **{impact_level} IMPACT**: {item.title}")
            summary_parts.append(f"   - {item.summary}")
            summary_parts.append("")
        
        if len(top_items) > 3:
            summary_parts.append(f"Additional {len(top_items) - 3} items are detailed in the full briefing below.")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _generate_key_insights(self, items: List[IntelligenceItem]) -> List[str]:
        """Generate key insights."""
        insights = []
        
        # Analyze trends
        high_impact_items = [item for item in items if item.impact_score >= 7]
        if high_impact_items:
            insights.append(f"**Critical Attention Required**: {len(high_impact_items)} high-impact events detected")
        
        # Analyze categories
        category_counts = {}
        for item in items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        if category_counts:
            top_category = max(category_counts, key=category_counts.get)
            insights.append(f"**Primary Focus Area**: {top_category.value.replace('_', ' ').title()} ({category_counts[top_category]} items)")
        
        # Analyze urgency
        urgent_items = [item for item in items if item.urgency_score >= 8]
        if urgent_items:
            insights.append(f"**Time-Sensitive Items**: {len(urgent_items)} items require immediate attention")
        
        # Analyze risk
        high_risk_items = [item for item in items if item.risk_score >= 7]
        if high_risk_items:
            insights.append(f"**Risk Exposure**: {len(high_risk_items)} items present elevated risk levels")
        
        # Source diversity
        source_counts = {}
        for item in items:
            source_counts[item.source] = source_counts.get(item.source, 0) + 1
        
        if len(source_counts) > 1:
            insights.append(f"**Source Diversity**: Intelligence confirmed across {len(source_counts)} independent sources")
        
        return insights if insights else ["No significant patterns detected in current intelligence"]
    
    def _generate_risk_assessment(self, items: List[IntelligenceItem]) -> str:
        """Generate risk assessment section."""
        if not items:
            return "**RISK ASSESSMENT**\n\nNo significant risks identified at this time."
        
        # Calculate overall risk metrics
        avg_risk = sum(item.risk_score for item in items) / len(items)
        high_risk_count = len([item for item in items if item.risk_score >= 7])
        
        risk_parts = [
            "**RISK ASSESSMENT**",
            "",
            f"**Overall Risk Level**: {'HIGH' if avg_risk >= 7 else 'MEDIUM' if avg_risk >= 4 else 'LOW'} (Score: {avg_risk:.1f}/10)",
            f"**High-Risk Items**: {high_risk_count}",
            ""
        ]
        
        # Top risk items
        high_risk_items = sorted([item for item in items if item.risk_score >= 6], 
                               key=lambda x: x.risk_score, reverse=True)[:3]
        
        if high_risk_items:
            risk_parts.append("**Primary Risk Exposures:**")
            for item in high_risk_items:
                risk_parts.append(f"- **{item.title}** (Risk: {item.risk_score:.1f}/10)")
                risk_parts.append(f"  {item.summary}")
            risk_parts.append("")
        
        # Risk mitigation recommendations
        risk_parts.extend([
            "**Risk Mitigation Priority:**",
            "1. Monitor high-impact developments for escalation potential",
            "2. Assess organizational exposure to identified risk factors", 
            "3. Prepare contingency responses for critical scenarios",
            "4. Enhance monitoring of related intelligence streams"
        ])
        
        return "\n".join(risk_parts)
    
    def _generate_recommendations(self, items: List[IntelligenceItem]) -> List[str]:
        """Generate action recommendations."""
        recommendations = []
        
        # High impact items
        high_impact = [item for item in items if item.impact_score >= 7]
        if high_impact:
            recommendations.append("**Immediate Actions**: Convene leadership team to assess implications of high-impact developments")
        
        # Urgent items
        urgent = [item for item in items if item.urgency_score >= 8]
        if urgent:
            recommendations.append("**Time-Critical**: Address urgent items within 24-48 hours")
        
        # Category-specific recommendations
        category_counts = {}
        for item in items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        if IntelligenceCategory.REGULATORY_CHANGE in category_counts:
            recommendations.append("**Compliance Review**: Engage legal and compliance teams to assess regulatory impact")
        
        if IntelligenceCategory.MARKET_SHOCK in category_counts:
            recommendations.append("**Financial Assessment**: Review portfolio exposure and hedging strategies")
        
        if IntelligenceCategory.AI_DEVELOPMENT in category_counts:
            recommendations.append("**Technology Strategy**: Evaluate implications for digital transformation roadmap")
        
        # Default recommendations
        if not recommendations:
            recommendations = [
                "**Continued Monitoring**: Maintain vigilance for developing situations",
                "**Stakeholder Communication**: Brief relevant teams on identified developments",
                "**Contingency Planning**: Review and update response protocols as needed"
            ]
        
        return recommendations
    
    def _generate_market_analysis(self, market_items: List[IntelligenceItem]) -> Optional[str]:
        """Generate market analysis section."""
        if not market_items:
            return None
        
        analysis_parts = [
            "**MARKET INTELLIGENCE**",
            "",
            f"**Market Activity**: {len(market_items)} significant market developments detected",
            ""
        ]
        
        # Analyze market sentiment
        high_impact_market = [item for item in market_items if item.impact_score >= 6]
        
        for item in high_impact_market[:3]:
            analysis_parts.append(f"**{item.title}**")
            analysis_parts.append(f"Impact: {item.impact_score:.1f}/10 | Risk: {item.risk_score:.1f}/10")
            analysis_parts.append(f"{item.summary}")
            analysis_parts.append("")
        
        analysis_parts.extend([
            "**Market Implications:**",
            "- Monitor for cascading effects across related sectors",
            "- Assess impact on key performance indicators",
            "- Consider hedging strategies for identified exposures"
        ])
        
        return "\n".join(analysis_parts)
    
    def _generate_regulatory_updates(self, regulatory_items: List[IntelligenceItem]) -> Optional[str]:
        """Generate regulatory updates section."""
        if not regulatory_items:
            return None
        
        updates_parts = [
            "**REGULATORY INTELLIGENCE**",
            "",
            f"**Regulatory Activity**: {len(regulatory_items)} regulatory developments identified",
            ""
        ]
        
        for item in regulatory_items[:3]:
            updates_parts.append(f"**{item.title}**")
            updates_parts.append(f"Urgency: {item.urgency_score:.1f}/10 | Impact: {item.impact_score:.1f}/10")
            updates_parts.append(f"{item.summary}")
            updates_parts.append("")
        
        updates_parts.extend([
            "**Compliance Considerations:**",
            "- Review current policies against new requirements",
            "- Assess implementation timelines and resource needs",
            "- Coordinate with legal and compliance teams",
            "- Monitor for additional guidance or clarifications"
        ])
        
        return "\n".join(updates_parts)
    
    def _generate_ai_intelligence(self, ai_items: List[IntelligenceItem]) -> Optional[str]:
        """Generate AI intelligence section."""
        if not ai_items:
            return None
        
        ai_parts = [
            "**AI & TECHNOLOGY INTELLIGENCE**",
            "",
            f"**AI Developments**: {len(ai_items)} artificial intelligence developments tracked",
            ""
        ]
        
        for item in ai_items[:3]:
            ai_parts.append(f"**{item.title}**")
            ai_parts.append(f"Innovation Impact: {item.impact_score:.1f}/10")
            ai_parts.append(f"{item.summary}")
            ai_parts.append("")
        
        ai_parts.extend([
            "**Strategic Implications:**",
            "- Evaluate competitive advantages and threats",
            "- Assess integration opportunities with current systems",
            "- Consider training and capability development needs",
            "- Monitor for regulatory responses to AI developments"
        ])
        
        return "\n".join(ai_parts)


class FeedManager:
    """Manages live intelligence feeds."""
    
    def __init__(self):
        self.feeds: Dict[str, LiveFeed] = {}
        
    def create_feed(self, name: str, description: str, 
                   categories: List[IntelligenceCategory],
                   is_premium: bool = False) -> LiveFeed:
        """Create a new intelligence feed."""
        feed_id = f"feed_{name.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}"
        
        feed = LiveFeed(
            id=feed_id,
            name=name,
            description=description,
            categories=categories,
            is_premium=is_premium
        )
        
        self.feeds[feed_id] = feed
        return feed
    
    def update_feed(self, feed_id: str, items: List[IntelligenceItem]) -> bool:
        """Update feed with new items."""
        if feed_id not in self.feeds:
            return False
        
        feed = self.feeds[feed_id]
        
        # Filter items by feed categories
        relevant_items = [
            item for item in items 
            if not feed.categories or item.category in feed.categories
        ]
        
        # Add new items (avoid duplicates)
        existing_ids = {item.id for item in feed.items}
        new_items = [item for item in relevant_items if item.id not in existing_ids]
        
        feed.items.extend(new_items)
        
        # Keep only last 100 items (or configurable limit)
        feed.items = feed.items[-100:]
        
        # Sort by timestamp (newest first)
        feed.items.sort(key=lambda x: x.timestamp, reverse=True)
        
        feed.last_updated = datetime.utcnow()
        
        logger.info(f"Updated feed {feed.name} with {len(new_items)} new items")
        return True
    
    def get_feed(self, feed_id: str) -> Optional[LiveFeed]:
        """Get feed by ID."""
        return self.feeds.get(feed_id)
    
    def list_feeds(self, include_premium: bool = True) -> List[LiveFeed]:
        """List all feeds."""
        feeds = list(self.feeds.values())
        if not include_premium:
            feeds = [feed for feed in feeds if not feed.is_premium]
        return feeds
    
    def get_filtered_items(self, feed_id: str, 
                          hours_back: int = 24,
                          min_impact: float = 0.0,
                          categories: Optional[List[IntelligenceCategory]] = None) -> List[IntelligenceItem]:
        """Get filtered items from a feed."""
        feed = self.feeds.get(feed_id)
        if not feed:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        filtered_items = [
            item for item in feed.items
            if (item.timestamp >= cutoff_time and 
                item.impact_score >= min_impact and
                (not categories or item.category in categories))
        ]
        
        return filtered_items


def create_default_feeds(feed_manager: FeedManager) -> List[LiveFeed]:
    """Create default intelligence feeds."""
    feeds = []
    
    # Executive Brief Feed (Premium)
    executive_feed = feed_manager.create_feed(
        name="Executive Intelligence Brief",
        description="High-impact intelligence for C-suite and senior leadership",
        categories=[
            IntelligenceCategory.MARKET_SHOCK,
            IntelligenceCategory.REGULATORY_CHANGE,
            IntelligenceCategory.POLITICAL_EVENT
        ],
        is_premium=True
    )
    feeds.append(executive_feed)
    
    # AI Development Feed
    ai_feed = feed_manager.create_feed(
        name="AI Development Monitor", 
        description="Latest developments in artificial intelligence and machine learning",
        categories=[IntelligenceCategory.AI_DEVELOPMENT],
        is_premium=False
    )
    feeds.append(ai_feed)
    
    # Market Intelligence Feed (Premium)
    market_feed = feed_manager.create_feed(
        name="Market Intelligence",
        description="Real-time market movements, volatility alerts, and financial intelligence",
        categories=[IntelligenceCategory.MARKET_SHOCK, IntelligenceCategory.VOLATILITY_ALERT],
        is_premium=True
    )
    feeds.append(market_feed)
    
    # Regulatory Watch Feed
    regulatory_feed = feed_manager.create_feed(
        name="Regulatory Watch",
        description="Regulatory changes, compliance updates, and policy shifts",
        categories=[IntelligenceCategory.REGULATORY_CHANGE, IntelligenceCategory.POLICY_SHIFT],
        is_premium=False
    )
    feeds.append(regulatory_feed)
    
    # Risk Intelligence Feed (Premium)
    risk_feed = feed_manager.create_feed(
        name="Risk Intelligence",
        description="Risk exposures, threat assessments, and black box discoveries",
        categories=[IntelligenceCategory.RISK_EXPOSURE, IntelligenceCategory.BLACK_BOX_DISCOVERY],
        is_premium=True
    )
    feeds.append(risk_feed)
    
    return feeds