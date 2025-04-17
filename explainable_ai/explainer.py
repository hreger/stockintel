import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

class StockExplainer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_names = [
            'price_momentum', 'volume_trend', 'rsi', 'macd',
            'pe_ratio', 'market_cap', 'sector_performance'
        ]
    
    def prepare_features(self, historical_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for model training and explanation"""
        # Calculate technical indicators
        data = historical_data.copy()
        data['price_momentum'] = data['price'].pct_change(periods=5)
        data['volume_trend'] = data['volume'].pct_change(periods=5)
        data['rsi'] = self._calculate_rsi(data['price'])
        data['macd'] = self._calculate_macd(data['price'])
        
        # Normalize features
        features = data[['price_momentum', 'volume_trend', 'rsi', 'macd']].values
        features = self.scaler.fit_transform(features)
        
        # Calculate target (next day's return)
        target = data['price'].pct_change().shift(-1).dropna()
        
        return features[:-1], target[:-1]  # Remove last row due to shift
    
    def train_model(self, features: np.ndarray, target: np.ndarray):
        """Train the model on historical data"""
        self.model.fit(features, target)
    
    def explain_prediction(self, features: np.ndarray) -> Dict:
        """Generate SHAP values and explanations for predictions"""
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(features)
        
        # Get feature importance
        feature_importance = np.abs(shap_values).mean(axis=0)
        importance_dict = dict(zip(self.feature_names, feature_importance))
        
        # Generate explanation
        explanation = self._generate_explanation(shap_values, features)
        
        return {
            'feature_importance': importance_dict,
            'explanation': explanation,
            'shap_values': shap_values.tolist()
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.Series) -> pd.Series:
        """Calculate Moving Average Convergence Divergence"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        return exp1 - exp2
    
    def _generate_explanation(self, shap_values: np.ndarray, features: np.ndarray) -> str:
        """Generate human-readable explanation of the prediction"""
        # Get the most important features
        feature_importance = np.abs(shap_values).mean(axis=0)
        top_features = np.argsort(feature_importance)[-3:][::-1]
        
        explanation_parts = []
        for feature_idx in top_features:
            feature_name = self.feature_names[feature_idx]
            shap_value = shap_values[0, feature_idx]
            feature_value = features[0, feature_idx]
            
            if feature_name == 'price_momentum':
                direction = "upward" if feature_value > 0 else "downward"
                explanation_parts.append(
                    f"Strong {direction} price momentum ({shap_value:.2f})"
                )
            elif feature_name == 'volume_trend':
                trend = "increasing" if feature_value > 0 else "decreasing"
                explanation_parts.append(
                    f"{trend.capitalize()} trading volume ({shap_value:.2f})"
                )
            elif feature_name == 'rsi':
                if feature_value > 70:
                    explanation_parts.append(
                        f"Overbought conditions (RSI: {feature_value:.1f}, impact: {shap_value:.2f})"
                    )
                elif feature_value < 30:
                    explanation_parts.append(
                        f"Oversold conditions (RSI: {feature_value:.1f}, impact: {shap_value:.2f})"
                    )
        
        return " ".join(explanation_parts) 