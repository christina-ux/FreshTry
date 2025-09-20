"""
Sample data generator for Live Intelligence Feed system.
Creates demo data for testing and demonstration purposes.
"""
import json
import random
from datetime import datetime, timedelta
from typing import List
from intelligence.models import (
    IntelligenceItem, IntelligenceMemo, TripwireRule, UserAction,
    IntelligenceCategory, IntelligenceSource
)


def generate_sample_intelligence_items(count: int = 50) -> List[IntelligenceItem]:
    """Generate sample intelligence items for testing."""
    items = []
    
    # Sample titles and content by category
    sample_data = {
        IntelligenceCategory.MARKET_SHOCK: [
            {
                "title": "Tech Stocks Plunge 15% Following AI Regulation Announcement",
                "content": "Major technology stocks experienced significant decline after new AI regulation framework was announced by federal authorities. The proposed regulations would require extensive compliance reporting for AI systems.",
                "tags": ["technology", "stocks", "AI", "regulation"]
            },
            {
                "title": "Federal Reserve Signals Emergency Rate Decision",
                "content": "Federal Reserve officials indicated potential emergency interest rate adjustment following unexpected inflation data. Market volatility increased significantly in pre-market trading.",
                "tags": ["federal_reserve", "interest_rates", "inflation", "markets"]
            },
            {
                "title": "Cryptocurrency Market Faces Massive Selloff",
                "content": "Bitcoin and other major cryptocurrencies dropped over 20% following regulatory crackdown announcements from multiple countries. Trading volumes reached historic highs.",
                "tags": ["cryptocurrency", "bitcoin", "regulation", "trading"]
            }
        ],
        
        IntelligenceCategory.REGULATORY_CHANGE: [
            {
                "title": "SEC Announces New AI Disclosure Requirements",
                "content": "Securities and Exchange Commission issued comprehensive guidelines requiring public companies to disclose AI system usage, risks, and governance frameworks in quarterly reports.",
                "tags": ["SEC", "AI", "disclosure", "compliance"]
            },
            {
                "title": "GDPR-Style Privacy Law Proposed for US Markets",
                "content": "Congressional committee introduced bipartisan legislation modeled after GDPR, requiring enhanced data protection measures and user consent mechanisms for all US companies.",
                "tags": ["privacy", "GDPR", "legislation", "data_protection"]
            },
            {
                "title": "FDA Issues Emergency Use Authorization Guidelines",
                "content": "Food and Drug Administration released updated emergency use authorization procedures for AI-enabled medical devices, streamlining approval processes while maintaining safety standards.",
                "tags": ["FDA", "medical_devices", "AI", "authorization"]
            }
        ],
        
        IntelligenceCategory.AI_DEVELOPMENT: [
            {
                "title": "OpenAI Releases GPT-5 with Revolutionary Capabilities",
                "content": "OpenAI unveiled GPT-5, demonstrating unprecedented reasoning abilities and multimodal processing. The model shows significant improvements in scientific research and complex problem-solving.",
                "tags": ["OpenAI", "GPT-5", "AI", "breakthrough"]
            },
            {
                "title": "Google Achieves Quantum AI Breakthrough",
                "content": "Google's quantum computing division announced successful demonstration of quantum machine learning algorithms, potentially revolutionizing drug discovery and financial modeling.",
                "tags": ["Google", "quantum", "AI", "machine_learning"]
            },
            {
                "title": "Microsoft Integrates Advanced AI into Enterprise Software",
                "content": "Microsoft announced comprehensive AI integration across Office 365, Azure, and enterprise tools, enabling automated workflow optimization and predictive analytics.",
                "tags": ["Microsoft", "enterprise", "Office365", "automation"]
            }
        ],
        
        IntelligenceCategory.POLITICAL_EVENT: [
            {
                "title": "Congressional AI Safety Hearing Reveals Bipartisan Concerns",
                "content": "House Committee on Science and Technology held emergency hearings on AI safety, with lawmakers expressing unified concern about autonomous weapon systems and election security.",
                "tags": ["Congress", "AI_safety", "weapons", "elections"]
            },
            {
                "title": "International AI Governance Summit Reaches Key Agreements",
                "content": "G7 nations signed preliminary agreement on international AI governance standards, establishing framework for cross-border AI system oversight and ethical guidelines.",
                "tags": ["G7", "international", "governance", "ethics"]
            }
        ],
        
        IntelligenceCategory.RISK_EXPOSURE: [
            {
                "title": "Critical Infrastructure Vulnerability Discovered",
                "content": "Cybersecurity researchers identified significant vulnerability in widely-used industrial control systems, potentially affecting power grids and water treatment facilities.",
                "tags": ["cybersecurity", "infrastructure", "vulnerability", "industrial"]
            },
            {
                "title": "Supply Chain Disruption Threatens Tech Manufacturing",
                "content": "Geopolitical tensions and natural disasters converged to create unprecedented supply chain disruptions, particularly affecting semiconductor and rare earth element availability.",
                "tags": ["supply_chain", "semiconductors", "manufacturing", "geopolitical"]
            }
        ]
    }
    
    # Generate items
    for i in range(count):
        category = random.choice(list(sample_data.keys()))
        sample_item = random.choice(sample_data[category])
        
        # Random timestamp within last 7 days
        timestamp = datetime.utcnow() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Random scores
        impact_score = random.uniform(3.0, 10.0)
        urgency_score = random.uniform(2.0, 9.0)
        risk_score = random.uniform(1.0, 8.0)
        confidence_score = random.uniform(0.6, 1.0)
        
        # Random source
        source = random.choice([
            IntelligenceSource.RSS_FEEDS,
            IntelligenceSource.WEB_SCRAPING,
            IntelligenceSource.REGULATORY_FEEDS,
            IntelligenceSource.TRIPWIRE_ALERTS
        ])
        
        item = IntelligenceItem(
            id=f"sample_{i}_{int(timestamp.timestamp())}",
            title=sample_item["title"],
            content=sample_item["content"],
            summary=sample_item["content"][:150] + "...",
            source=source,
            category=category,
            confidence_score=confidence_score,
            impact_score=impact_score,
            urgency_score=urgency_score,
            risk_score=risk_score,
            timestamp=timestamp,
            tags=sample_item["tags"],
            source_url=f"https://example.com/article/{i}",
            metadata={
                "sample_data": True,
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
        items.append(item)
    
    return items


def generate_sample_user_actions(user_count: int = 10, action_count: int = 100) -> List[UserAction]:
    """Generate sample user actions for testing learning system."""
    actions = []
    
    action_types = ["click", "read", "bookmark", "share", "dismiss"]
    target_types = ["intelligence_item", "memo", "feed"]
    
    for i in range(action_count):
        user_id = f"user_{random.randint(1, user_count)}"
        action_type = random.choice(action_types)
        target_type = random.choice(target_types)
        target_id = f"target_{random.randint(1, 50)}"
        
        # Random timestamp within last 30 days
        timestamp = datetime.utcnow() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Generate relevant metadata
        metadata = {
            "category": random.choice(list(IntelligenceCategory)).value,
            "source": random.choice(list(IntelligenceSource)).value,
            "session_duration": random.randint(30, 600),  # seconds
            "sample_data": True
        }
        
        if action_type == "read":
            metadata["reading_time_seconds"] = random.randint(30, 300)
        
        action = UserAction(
            id=f"action_{i}_{int(timestamp.timestamp())}",
            user_id=user_id,
            action_type=action_type,
            target_id=target_id,
            target_type=target_type,
            timestamp=timestamp,
            metadata=metadata
        )
        
        actions.append(action)
    
    return actions


def generate_sample_memo() -> IntelligenceMemo:
    """Generate a sample intelligence memo."""
    
    sample_items = generate_sample_intelligence_items(10)
    
    memo = IntelligenceMemo(
        id=f"sample_memo_{int(datetime.utcnow().timestamp())}",
        title="Daily Intelligence Brief - Sample Report",
        executive_summary="""**EXECUTIVE SUMMARY**

This briefing covers 3 priority intelligence items requiring executive attention:

1. **HIGH IMPACT**: Tech Stocks Plunge 15% Following AI Regulation Announcement
   - Major technology stocks experienced significant decline after new AI regulation framework was announced by federal authorities.

2. **HIGH IMPACT**: SEC Announces New AI Disclosure Requirements  
   - Securities and Exchange Commission issued comprehensive guidelines requiring public companies to disclose AI system usage, risks, and governance frameworks.

3. **MEDIUM IMPACT**: OpenAI Releases GPT-5 with Revolutionary Capabilities
   - OpenAI unveiled GPT-5, demonstrating unprecedented reasoning abilities and multimodal processing.

Additional 7 items are detailed in the full briefing below.""",
        
        key_insights=[
            "**Critical Attention Required**: 3 high-impact events detected",
            "**Primary Focus Area**: Regulatory Change (4 items)", 
            "**Time-Sensitive Items**: 2 items require immediate attention",
            "**Risk Exposure**: 3 items present elevated risk levels",
            "**Source Diversity**: Intelligence confirmed across 4 independent sources"
        ],
        
        risk_assessment="""**RISK ASSESSMENT**

**Overall Risk Level**: HIGH (Score: 7.2/10)
**High-Risk Items**: 3

**Primary Risk Exposures:**
- **Tech Stocks Plunge 15% Following AI Regulation Announcement** (Risk: 8.5/10)
  Major technology stocks experienced significant decline after new AI regulation framework was announced.
- **Critical Infrastructure Vulnerability Discovered** (Risk: 7.8/10)
  Cybersecurity researchers identified significant vulnerability in widely-used industrial control systems.
- **Supply Chain Disruption Threatens Tech Manufacturing** (Risk: 7.2/10)
  Geopolitical tensions and natural disasters converged to create unprecedented supply chain disruptions.

**Risk Mitigation Priority:**
1. Monitor high-impact developments for escalation potential
2. Assess organizational exposure to identified risk factors
3. Prepare contingency responses for critical scenarios
4. Enhance monitoring of related intelligence streams""",
        
        recommendations=[
            "**Immediate Actions**: Convene leadership team to assess implications of high-impact developments",
            "**Time-Critical**: Address urgent items within 24-48 hours",
            "**Compliance Review**: Engage legal and compliance teams to assess regulatory impact",
            "**Financial Assessment**: Review portfolio exposure and hedging strategies",
            "**Technology Strategy**: Evaluate implications for digital transformation roadmap"
        ],
        
        market_analysis="""**MARKET INTELLIGENCE**

**Market Activity**: 3 significant market developments detected

**Tech Stocks Plunge 15% Following AI Regulation Announcement**
Impact: 9.2/10 | Risk: 8.5/10
Major technology stocks experienced significant decline after new AI regulation framework was announced by federal authorities.

**Federal Reserve Signals Emergency Rate Decision**
Impact: 8.7/10 | Risk: 7.8/10  
Federal Reserve officials indicated potential emergency interest rate adjustment following unexpected inflation data.

**Market Implications:**
- Monitor for cascading effects across related sectors
- Assess impact on key performance indicators
- Consider hedging strategies for identified exposures""",
        
        regulatory_updates="""**REGULATORY INTELLIGENCE**

**Regulatory Activity**: 2 regulatory developments identified

**SEC Announces New AI Disclosure Requirements**
Urgency: 8.5/10 | Impact: 8.2/10
Securities and Exchange Commission issued comprehensive guidelines requiring public companies to disclose AI system usage.

**GDPR-Style Privacy Law Proposed for US Markets**
Urgency: 6.5/10 | Impact: 7.8/10
Congressional committee introduced bipartisan legislation modeled after GDPR, requiring enhanced data protection measures.

**Compliance Considerations:**
- Review current policies against new requirements
- Assess implementation timelines and resource needs
- Coordinate with legal and compliance teams
- Monitor for additional guidance or clarifications""",
        
        ai_intelligence="""**AI & TECHNOLOGY INTELLIGENCE**

**AI Developments**: 2 artificial intelligence developments tracked

**OpenAI Releases GPT-5 with Revolutionary Capabilities**
Innovation Impact: 9.5/10
OpenAI unveiled GPT-5, demonstrating unprecedented reasoning abilities and multimodal processing.

**Google Achieves Quantum AI Breakthrough**
Innovation Impact: 8.8/10
Google's quantum computing division announced successful demonstration of quantum machine learning algorithms.

**Strategic Implications:**
- Evaluate competitive advantages and threats
- Assess integration opportunities with current systems
- Consider training and capability development needs
- Monitor for regulatory responses to AI developments""",
        
        sources=sample_items,
        memo_type="daily",
        target_audience="executive"
    )
    
    return memo


def populate_sample_data(output_dir: str = "data/sample"):
    """Generate and save sample data to files."""
    import os
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate sample data
    intelligence_items = generate_sample_intelligence_items(50)
    user_actions = generate_sample_user_actions(10, 100)
    sample_memo = generate_sample_memo()
    
    # Save to JSON files
    with open(f"{output_dir}/intelligence_items.json", "w") as f:
        json.dump([item.dict() for item in intelligence_items], f, indent=2, default=str)
    
    with open(f"{output_dir}/user_actions.json", "w") as f:
        json.dump([action.dict() for action in user_actions], f, indent=2, default=str)
    
    with open(f"{output_dir}/sample_memo.json", "w") as f:
        json.dump(sample_memo.dict(), f, indent=2, default=str)
    
    print(f"Sample data generated and saved to {output_dir}/")
    print(f"- {len(intelligence_items)} intelligence items")
    print(f"- {len(user_actions)} user actions")
    print(f"- 1 sample memo")


if __name__ == "__main__":
    populate_sample_data()