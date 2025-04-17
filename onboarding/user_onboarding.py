import json
from typing import Dict, List, Optional
from pathlib import Path
import yaml

class UserPreferences:
    def __init__(self):
        self.preferences = {
            'risk_tolerance': 'medium',  # low, medium, high
            'investment_horizon': 'long_term',  # short_term, medium_term, long_term
            'preferred_sectors': [],
            'watchlist': [],
            'notification_preferences': {
                'price_alerts': True,
                'portfolio_updates': True,
                'market_news': True
            }
        }
        self.config_path = Path('user_config')
        self.config_path.mkdir(exist_ok=True)
    
    def save_preferences(self, user_id: str):
        """Save user preferences to a YAML file"""
        file_path = self.config_path / f'{user_id}_preferences.yaml'
        with open(file_path, 'w') as f:
            yaml.dump(self.preferences, f)
    
    def load_preferences(self, user_id: str) -> Dict:
        """Load user preferences from YAML file"""
        file_path = self.config_path / f'{user_id}_preferences.yaml'
        if file_path.exists():
            with open(file_path, 'r') as f:
                self.preferences = yaml.safe_load(f)
        return self.preferences
    
    def update_preferences(self, updates: Dict):
        """Update user preferences"""
        self.preferences.update(updates)
    
    def get_recommended_portfolio(self) -> Dict[str, float]:
        """Get recommended portfolio based on user preferences"""
        # Base allocations for different risk levels
        risk_allocations = {
            'low': {
                'Bonds': 0.6,
                'Large Cap': 0.3,
                'Cash': 0.1
            },
            'medium': {
                'Large Cap': 0.5,
                'Mid Cap': 0.3,
                'Bonds': 0.2
            },
            'high': {
                'Large Cap': 0.4,
                'Mid Cap': 0.3,
                'Small Cap': 0.2,
                'International': 0.1
            }
        }
        
        # Adjust based on investment horizon
        horizon_adjustments = {
            'short_term': {'Cash': 0.2, 'Bonds': 0.3},
            'medium_term': {'Cash': 0.1, 'Bonds': 0.2},
            'long_term': {'Cash': 0.05, 'Bonds': 0.1}
        }
        
        # Get base allocation
        allocation = risk_allocations[self.preferences['risk_tolerance']].copy()
        
        # Apply horizon adjustments
        horizon = self.preferences['investment_horizon']
        for asset, adjustment in horizon_adjustments[horizon].items():
            if asset in allocation:
                allocation[asset] += adjustment
        
        # Normalize to ensure weights sum to 1
        total = sum(allocation.values())
        allocation = {k: v/total for k, v in allocation.items()}
        
        return allocation
    
    def get_recommended_stocks(self) -> List[str]:
        """Get recommended stocks based on user preferences"""
        # This would typically come from a more sophisticated recommendation engine
        # For now, using a simple mapping
        sector_stocks = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL'],
            'Finance': ['JPM', 'BAC', 'GS'],
            'Healthcare': ['JNJ', 'PFE', 'UNH'],
            'Consumer': ['PG', 'KO', 'MCD']
        }
        
        recommended = []
        for sector in self.preferences['preferred_sectors']:
            if sector in sector_stocks:
                recommended.extend(sector_stocks[sector])
        
        return recommended[:5]  # Return top 5 recommendations 