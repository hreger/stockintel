from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import sqlite3
from datetime import datetime

@dataclass
class UserPreference:
    user_id: str
    theme: str
    default_timeframe: str
    chart_preferences: Dict
    notification_settings: Dict
    feature_level: str  # basic, intermediate, advanced

class UserExperienceManager:
    def __init__(self):
        self.db_path = 'user_preferences.db'
        self.feature_tiers = {
            'basic': self._get_basic_features(),
            'intermediate': self._get_intermediate_features(),
            'advanced': self._get_advanced_features()
        }
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                preferences TEXT,
                last_updated TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        
    def get_user_flow(self, user_level: str) -> List[Dict]:
        """Get personalized user flow based on experience level"""
        return {
            'basic': [
                {'step': 'Welcome', 'content': self._get_welcome_tutorial()},
                {'step': 'Basic Charts', 'content': self._get_chart_tutorial()},
                {'step': 'Portfolio Overview', 'content': self._get_portfolio_tutorial()},
                {'step': 'First Trade', 'content': self._get_trading_tutorial()}
            ],
            'intermediate': [
                {'step': 'Technical Analysis', 'content': self._get_technical_tutorial()},
                {'step': 'Risk Management', 'content': self._get_risk_tutorial()},
                {'step': 'Advanced Charts', 'content': self._get_advanced_chart_tutorial()}
            ],
            'advanced': [
                {'step': 'API Integration', 'content': self._get_api_tutorial()},
                {'step': 'Custom Strategies', 'content': self._get_strategy_tutorial()},
                {'step': 'Automation', 'content': self._get_automation_tutorial()}
            ]
        }[user_level]
        
    def save_user_preferences(self, preferences: UserPreference):
        """Save user preferences to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, preferences, last_updated)
            VALUES (?, ?, ?)
        ''', (
            preferences.user_id,
            json.dumps(preferences.__dict__),
            datetime.now()
        ))
        conn.commit()
        conn.close()
        
    def get_interactive_tutorial(self, feature: str) -> Dict:
        """Get interactive tutorial content"""
        return {
            'title': f"Learning {feature}",
            'steps': self._get_tutorial_steps(feature),
            'interactive_elements': self._get_interactive_elements(feature),
            'completion_criteria': self._get_completion_criteria(feature)
        }
        
    def _get_tutorial_steps(self, feature: str) -> List[Dict]:
        """Get step-by-step tutorial content"""
        return [
            {
                'step': 1,
                'title': 'Introduction',
                'content': f"Welcome to {feature}",
                'interactive': True,
                'validation': self._validate_step_completion
            },
            # Additional steps based on feature
        ]
        
    def _get_basic_features(self) -> List[str]:
        """Define basic feature set"""
        return [
            'portfolio_overview',
            'basic_charts',
            'market_overview',
            'simple_trading'
        ]
        
    def _get_intermediate_features(self) -> List[str]:
        """Define intermediate feature set"""
        return [
            'technical_indicators',
            'risk_management',
            'advanced_charts',
            'portfolio_analysis'
        ]
        
    def _get_advanced_features(self) -> List[str]:
        """Define advanced feature set"""
        return [
            'api_integration',
            'custom_strategies',
            'automated_trading',
            'advanced_analytics'
        ]
        
    def collect_user_feedback(self, user_id: str, feature: str, feedback: Dict):
        """Collect and store user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                user_id TEXT,
                feature TEXT,
                feedback TEXT,
                timestamp TIMESTAMP
            )
        ''')
        cursor.execute('''
            INSERT INTO user_feedback (user_id, feature, feedback, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            user_id,
            feature,
            json.dumps(feedback),
            datetime.now()
        ))
        conn.commit()
        conn.close()