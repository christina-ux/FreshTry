"""
Self-evolving intelligence system with user action tracking and learning loops.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json
from collections import defaultdict, Counter
import statistics

from .models import (
    UserAction, LearningDelta, IntelligenceItem, TripwireRule, 
    IntelligenceCategory, IntelligenceSource
)

logger = logging.getLogger(__name__)


class ActionTracker:
    """Tracks user actions for learning and personalization."""
    
    def __init__(self):
        self.actions: List[UserAction] = []
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        
    def track_action(self, user_id: str, action_type: str, target_id: str, 
                    target_type: str, metadata: Optional[Dict[str, Any]] = None) -> UserAction:
        """Track a user action."""
        action = UserAction(
            id=f"action_{len(self.actions)}_{int(datetime.utcnow().timestamp())}",
            user_id=user_id,
            action_type=action_type,
            target_id=target_id,
            target_type=target_type,
            metadata=metadata or {}
        )
        
        self.actions.append(action)
        
        # Update user preferences in real-time
        self._update_user_preferences(action)
        
        logger.info(f"Tracked action: {action_type} by user {user_id} on {target_type} {target_id}")
        return action
    
    def get_user_actions(self, user_id: str, 
                        hours_back: int = 24,
                        action_types: Optional[List[str]] = None) -> List[UserAction]:
        """Get user actions within a time window."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        return [
            action for action in self.actions
            if (action.user_id == user_id and 
                action.timestamp >= cutoff_time and
                (not action_types or action.action_type in action_types))
        ]
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get learned preferences for a user."""
        return self.user_preferences.get(user_id, {})
    
    def _update_user_preferences(self, action: UserAction):
        """Update user preferences based on action."""
        user_id = action.user_id
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'preferred_categories': Counter(),
                'preferred_sources': Counter(),
                'reading_behavior': {
                    'avg_reading_time': 0,
                    'preferred_content_length': 'medium',
                    'active_hours': Counter()
                },
                'engagement_patterns': {
                    'bookmark_rate': 0,
                    'share_rate': 0,
                    'click_through_rate': 0
                }
            }
        
        prefs = self.user_preferences[user_id]
        
        # Update category preferences based on engagement
        if action.action_type in ['click', 'read', 'bookmark', 'share']:
            category = action.metadata.get('category')
            if category:
                prefs['preferred_categories'][category] += 1
        
        # Update source preferences
        if action.action_type in ['click', 'read']:
            source = action.metadata.get('source')
            if source:
                prefs['preferred_sources'][source] += 1
        
        # Update reading behavior
        if action.action_type == 'read':
            reading_time = action.metadata.get('reading_time_seconds', 0)
            if reading_time > 0:
                current_avg = prefs['reading_behavior']['avg_reading_time']
                # Simple moving average
                prefs['reading_behavior']['avg_reading_time'] = (current_avg * 0.8) + (reading_time * 0.2)
        
        # Track active hours
        hour = action.timestamp.hour
        prefs['reading_behavior']['active_hours'][hour] += 1
        
        # Update engagement patterns
        if action.action_type == 'bookmark':
            prefs['engagement_patterns']['bookmark_rate'] += 0.1
        elif action.action_type == 'share':
            prefs['engagement_patterns']['share_rate'] += 0.1
        elif action.action_type == 'click':
            prefs['engagement_patterns']['click_through_rate'] += 0.05


class LearningEngine:
    """Self-evolving learning engine that updates system behavior based on user actions."""
    
    def __init__(self, action_tracker: ActionTracker):
        self.action_tracker = action_tracker
        self.learning_deltas: List[LearningDelta] = []
        self.system_parameters: Dict[str, Any] = self._initialize_parameters()
        
    def _initialize_parameters(self) -> Dict[str, Any]:
        """Initialize system parameters."""
        return {
            'scoring_weights': {
                'impact_weight': 0.4,
                'urgency_weight': 0.3,
                'risk_weight': 0.2,
                'confidence_weight': 0.1
            },
            'category_importance': {
                category.value: 1.0 for category in IntelligenceCategory
            },
            'source_credibility': {
                source.value: 1.0 for source in IntelligenceSource
            },
            'tripwire_sensitivity': 0.7,
            'personalization_strength': 0.5
        }
    
    def analyze_and_learn(self, lookback_hours: int = 24) -> List[LearningDelta]:
        """Analyze recent user actions and generate learning deltas."""
        cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        recent_actions = [
            action for action in self.action_tracker.actions
            if action.timestamp >= cutoff_time
        ]
        
        if not recent_actions:
            return []
        
        deltas = []
        
        # Learn from user engagement patterns
        engagement_deltas = self._learn_from_engagement(recent_actions)
        deltas.extend(engagement_deltas)
        
        # Learn from content preferences
        content_deltas = self._learn_from_content_preferences(recent_actions)
        deltas.extend(content_deltas)
        
        # Learn from timing patterns
        timing_deltas = self._learn_from_timing_patterns(recent_actions)
        deltas.extend(timing_deltas)
        
        # Update tripwire sensitivities
        tripwire_deltas = self._learn_tripwire_sensitivity(recent_actions)
        deltas.extend(tripwire_deltas)
        
        # Apply all deltas
        for delta in deltas:
            self._apply_delta(delta)
        
        self.learning_deltas.extend(deltas)
        
        logger.info(f"Generated {len(deltas)} learning deltas from {len(recent_actions)} recent actions")
        return deltas
    
    def _learn_from_engagement(self, actions: List[UserAction]) -> List[LearningDelta]:
        """Learn from user engagement patterns."""
        deltas = []
        
        # Analyze which categories get more engagement
        category_engagement = defaultdict(list)
        
        for action in actions:
            if action.action_type in ['bookmark', 'share', 'read']:
                category = action.metadata.get('category')
                if category:
                    # Higher score for more engaging actions
                    engagement_score = {'read': 1, 'bookmark': 2, 'share': 3}.get(action.action_type, 1)
                    category_engagement[category].append(engagement_score)
        
        # Update category importance based on engagement
        for category, scores in category_engagement.items():
            if len(scores) >= 3:  # Need minimum data points
                avg_engagement = statistics.mean(scores)
                current_importance = self.system_parameters['category_importance'].get(category, 1.0)
                
                # Adjust importance based on engagement
                new_importance = current_importance * (0.9 + (avg_engagement / 10))
                new_importance = max(0.1, min(2.0, new_importance))  # Bound between 0.1 and 2.0
                
                if abs(new_importance - current_importance) > 0.05:  # Significant change
                    delta = LearningDelta(
                        id=f"delta_category_importance_{category}_{int(datetime.utcnow().timestamp())}",
                        change_type="category_importance_update",
                        description=f"Updated importance for category {category} based on user engagement",
                        before_state={"category": category, "importance": current_importance},
                        after_state={"category": category, "importance": new_importance},
                        confidence=min(len(scores) / 10, 1.0),  # More actions = higher confidence
                        source_actions=[action.id for action in actions if action.metadata.get('category') == category]
                    )
                    deltas.append(delta)
        
        return deltas
    
    def _learn_from_content_preferences(self, actions: List[UserAction]) -> List[LearningDelta]:
        """Learn from content preferences."""
        deltas = []
        
        # Analyze source credibility based on user actions
        source_interactions = defaultdict(list)
        
        for action in actions:
            source = action.metadata.get('source')
            if source and action.action_type in ['click', 'read', 'bookmark', 'share']:
                # Score based on action depth
                interaction_score = {
                    'click': 1, 'read': 2, 'bookmark': 3, 'share': 4
                }.get(action.action_type, 1)
                source_interactions[source].append(interaction_score)
        
        # Update source credibility
        for source, scores in source_interactions.items():
            if len(scores) >= 2:  # Minimum interactions
                avg_score = statistics.mean(scores)
                current_credibility = self.system_parameters['source_credibility'].get(source, 1.0)
                
                # Adjust credibility (sources with higher engagement get higher credibility)
                credibility_factor = 0.8 + (avg_score / 10)
                new_credibility = current_credibility * credibility_factor
                new_credibility = max(0.1, min(2.0, new_credibility))
                
                if abs(new_credibility - current_credibility) > 0.05:
                    delta = LearningDelta(
                        id=f"delta_source_credibility_{source}_{int(datetime.utcnow().timestamp())}",
                        change_type="source_credibility_update",
                        description=f"Updated credibility for source {source} based on user interactions",
                        before_state={"source": source, "credibility": current_credibility},
                        after_state={"source": source, "credibility": new_credibility},
                        confidence=min(len(scores) / 5, 1.0),
                        source_actions=[action.id for action in actions if action.metadata.get('source') == source]
                    )
                    deltas.append(delta)
        
        return deltas
    
    def _learn_from_timing_patterns(self, actions: List[UserAction]) -> List[LearningDelta]:
        """Learn from timing patterns to optimize delivery."""
        deltas = []
        
        # Analyze when users are most active
        hourly_activity = Counter()
        high_engagement_hours = Counter()
        
        for action in actions:
            hour = action.timestamp.hour
            hourly_activity[hour] += 1
            
            if action.action_type in ['bookmark', 'share']:
                high_engagement_hours[hour] += 1
        
        if hourly_activity and high_engagement_hours:
            # Find peak engagement hours
            peak_hours = [hour for hour, count in high_engagement_hours.most_common(3)]
            
            if peak_hours:
                delta = LearningDelta(
                    id=f"delta_timing_optimization_{int(datetime.utcnow().timestamp())}",
                    change_type="timing_optimization",
                    description="Updated optimal delivery timing based on user engagement patterns",
                    before_state={"peak_hours": []},
                    after_state={"peak_hours": peak_hours},
                    confidence=min(len(actions) / 20, 1.0),
                    source_actions=[action.id for action in actions]
                )
                deltas.append(delta)
        
        return deltas
    
    def _learn_tripwire_sensitivity(self, actions: List[UserAction]) -> List[LearningDelta]:
        """Learn optimal tripwire sensitivity from user responses."""
        deltas = []
        
        # Analyze responses to tripwire alerts
        tripwire_responses = defaultdict(list)
        
        for action in actions:
            if action.target_type == 'intelligence_item' and action.metadata.get('source') == 'tripwire_alerts':
                tripwire_id = action.metadata.get('tripwire_id')
                if tripwire_id:
                    # Score based on user response
                    response_score = {
                        'dismiss': -1, 'click': 1, 'read': 2, 'bookmark': 3, 'share': 4
                    }.get(action.action_type, 0)
                    tripwire_responses[tripwire_id].append(response_score)
        
        # Adjust tripwire sensitivity based on responses
        for tripwire_id, scores in tripwire_responses.items():
            if len(scores) >= 2:
                avg_response = statistics.mean(scores)
                
                # If users consistently ignore (negative scores), increase threshold
                # If users engage (positive scores), maintain or decrease threshold
                current_sensitivity = self.system_parameters.get('tripwire_sensitivity', 0.7)
                
                if avg_response < 0:  # Users dismissing alerts
                    new_sensitivity = max(0.1, current_sensitivity - 0.1)
                elif avg_response > 1:  # Users engaging with alerts
                    new_sensitivity = min(1.0, current_sensitivity + 0.05)
                else:
                    continue  # No significant change needed
                
                delta = LearningDelta(
                    id=f"delta_tripwire_sensitivity_{tripwire_id}_{int(datetime.utcnow().timestamp())}",
                    change_type="tripwire_sensitivity_update",
                    description=f"Updated tripwire sensitivity for {tripwire_id} based on user responses",
                    before_state={"tripwire_id": tripwire_id, "sensitivity": current_sensitivity},
                    after_state={"tripwire_id": tripwire_id, "sensitivity": new_sensitivity},
                    confidence=min(len(scores) / 5, 1.0),
                    source_actions=[action.id for action in actions if action.metadata.get('tripwire_id') == tripwire_id]
                )
                deltas.append(delta)
        
        return deltas
    
    def _apply_delta(self, delta: LearningDelta):
        """Apply a learning delta to system parameters."""
        try:
            if delta.change_type == "category_importance_update":
                category = delta.after_state["category"]
                importance = delta.after_state["importance"]
                self.system_parameters['category_importance'][category] = importance
                
            elif delta.change_type == "source_credibility_update":
                source = delta.after_state["source"]
                credibility = delta.after_state["credibility"]
                self.system_parameters['source_credibility'][source] = credibility
                
            elif delta.change_type == "tripwire_sensitivity_update":
                sensitivity = delta.after_state["sensitivity"]
                self.system_parameters['tripwire_sensitivity'] = sensitivity
                
            elif delta.change_type == "timing_optimization":
                # Store peak hours for delivery optimization
                peak_hours = delta.after_state["peak_hours"]
                self.system_parameters['optimal_delivery_hours'] = peak_hours
            
            logger.info(f"Applied learning delta: {delta.change_type}")
            
        except Exception as e:
            logger.error(f"Error applying delta {delta.id}: {e}")
    
    def get_personalized_scoring(self, user_id: str, item: IntelligenceItem) -> float:
        """Get personalized scoring for an intelligence item."""
        base_score = (
            item.impact_score * self.system_parameters['scoring_weights']['impact_weight'] +
            item.urgency_score * self.system_parameters['scoring_weights']['urgency_weight'] +
            item.risk_score * self.system_parameters['scoring_weights']['risk_weight'] +
            item.confidence_score * 10 * self.system_parameters['scoring_weights']['confidence_weight']
        )
        
        # Apply personalization
        user_prefs = self.action_tracker.get_user_preferences(user_id)
        if user_prefs:
            # Category preference boost
            category_boost = user_prefs['preferred_categories'].get(item.category.value, 0) / 10
            
            # Source credibility adjustment
            source_credibility = self.system_parameters['source_credibility'].get(item.source.value, 1.0)
            
            # Apply personalization
            personalization_factor = self.system_parameters['personalization_strength']
            personalized_score = base_score * (1 + (category_boost * personalization_factor)) * source_credibility
            
            return min(personalized_score, 10.0)  # Cap at 10
        
        return base_score
    
    def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get metrics about the learning system's health."""
        return {
            'total_actions_tracked': len(self.action_tracker.actions),
            'total_learning_deltas': len(self.learning_deltas),
            'unique_users': len(set(action.user_id for action in self.action_tracker.actions)),
            'avg_deltas_per_day': len([
                delta for delta in self.learning_deltas 
                if delta.applied_at >= datetime.utcnow() - timedelta(days=1)
            ]),
            'system_parameters': self.system_parameters,
            'last_learning_cycle': max([delta.applied_at for delta in self.learning_deltas]) if self.learning_deltas else None
        }


class ContinuousLearningOrchestrator:
    """Orchestrates continuous learning cycles."""
    
    def __init__(self, learning_engine: LearningEngine, interval_hours: int = 6):
        self.learning_engine = learning_engine
        self.interval_hours = interval_hours
        self.last_learning_cycle = datetime.utcnow()
        
    async def run_learning_cycle(self) -> Dict[str, Any]:
        """Run a complete learning cycle."""
        start_time = datetime.utcnow()
        
        # Generate learning deltas
        deltas = self.learning_engine.analyze_and_learn(lookback_hours=self.interval_hours)
        
        # Get system health
        health_metrics = self.learning_engine.get_system_health_metrics()
        
        self.last_learning_cycle = start_time
        
        cycle_results = {
            'cycle_start': start_time,
            'deltas_generated': len(deltas),
            'deltas': [
                {
                    'id': delta.id,
                    'type': delta.change_type,
                    'description': delta.description,
                    'confidence': delta.confidence
                } for delta in deltas
            ],
            'system_health': health_metrics,
            'next_cycle_due': start_time + timedelta(hours=self.interval_hours)
        }
        
        logger.info(f"Completed learning cycle: {len(deltas)} deltas generated")
        return cycle_results
    
    def should_run_cycle(self) -> bool:
        """Check if it's time to run another learning cycle."""
        return datetime.utcnow() >= self.last_learning_cycle + timedelta(hours=self.interval_hours)