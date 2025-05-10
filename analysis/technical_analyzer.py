from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class TechnicalSignal:
    indicator: str
    signal: str
    strength: float
    confidence: float
    limitations: List[str]

class TechnicalAnalyzer:
    def __init__(self):
        self.trend_threshold = 0.02  # 2% threshold for trend confirmation
        self.stop_loss_default = 0.05  # 5% default stop loss
        
    def analyze_stock(self, data: pd.DataFrame, include_fundamentals: bool = True) -> Dict:
        """
        Multi-factor technical analysis with risk management
        
        Args:
            data: DataFrame with OHLCV data
            include_fundamentals: Whether to include fundamental metrics
        """
        signals = []
        
        # Multiple timeframe analysis
        short_trend = self._analyze_trend(data, window=20)
        medium_trend = self._analyze_trend(data, window=50)
        long_trend = self._analyze_trend(data, window=200)
        
        # Trend alignment check
        trend_alignment = self._check_trend_alignment(short_trend, medium_trend, long_trend)
        
        # Technical indicators with confidence scores
        signals.extend([
            self._analyze_moving_averages(data),
            self._analyze_momentum(data),
            self._analyze_volume(data),
            self._analyze_volatility(data)
        ])
        
        # Risk metrics
        risk_metrics = self._calculate_risk_metrics(data)
        
        # Stop loss recommendations
        stop_loss = self._calculate_stop_loss(data, risk_metrics)
        
        return {
            'overall_signal': self._combine_signals(signals, trend_alignment),
            'individual_signals': signals,
            'risk_metrics': risk_metrics,
            'stop_loss': stop_loss,
            'limitations': self._get_analysis_limitations(data)
        }
        
    def _analyze_trend(self, data: pd.DataFrame, window: int) -> Dict:
        """Analyze trend with multiple confirmation factors"""
        ma = data['close'].rolling(window=window).mean()
        slope = (ma - ma.shift(5)) / ma.shift(5)
        
        return {
            'direction': 'up' if slope.iloc[-1] > self.trend_threshold else 'down',
            'strength': abs(slope.iloc[-1]),
            'consistency': self._calculate_trend_consistency(slope)
        }
        
    def _check_trend_alignment(self, short: Dict, medium: Dict, long: Dict) -> Dict:
        """Check alignment across multiple timeframes"""
        aligned = (short['direction'] == medium['direction'] == long['direction'])
        return {
            'aligned': aligned,
            'confidence': (short['consistency'] + medium['consistency'] + long['consistency']) / 3,
            'primary_trend': long['direction']
        }
        
    def _calculate_risk_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate comprehensive risk metrics"""
        returns = data['close'].pct_change()
        
        return {
            'volatility': returns.std() * np.sqrt(252),  # Annualized volatility
            'max_drawdown': self._calculate_max_drawdown(data['close']),
            'var_95': returns.quantile(0.05),  # 95% VaR
            'risk_reward_ratio': self._calculate_risk_reward_ratio(returns)
        }
        
    def _calculate_stop_loss(self, data: pd.DataFrame, risk_metrics: Dict) -> Dict:
        """Dynamic stop loss calculation"""
        atr = self._calculate_atr(data)
        volatility_based = atr * 2
        
        return {
            'technical_stop': min(volatility_based, self.stop_loss_default),
            'risk_adjusted_stop': self._adjust_stop_loss(volatility_based, risk_metrics),
            'trailing_stop': self._calculate_trailing_stop(data, atr)
        }
        
    def _get_analysis_limitations(self, data: pd.DataFrame) -> List[str]:
        """Document technical analysis limitations"""
        limitations = [
            "Technical indicators are lagging by nature",
            "Past performance doesn't guarantee future results",
            "Signals may conflict during ranging markets",
            "Effectiveness varies with market conditions",
            "Limited predictive power during extreme events"
        ]
        
        if len(data) < 200:
            limitations.append("Limited historical data may affect accuracy")
            
        return limitations
        
    def _combine_signals(self, signals: List[TechnicalSignal], trend_alignment: Dict) -> Dict:
        """Weight and combine multiple technical signals"""
        weighted_score = 0
        total_weight = 0
        
        for signal in signals:
            weight = signal.confidence * (1.5 if trend_alignment['aligned'] else 1.0)
            weighted_score += signal.strength * weight
            total_weight += weight
            
        return {
            'signal': 'buy' if weighted_score > 0 else 'sell',
            'strength': abs(weighted_score / total_weight),
            'confidence': trend_alignment['confidence'],
            'against_trend': self._check_against_trend(weighted_score, trend_alignment)
        }
        
    def _check_against_trend(self, signal_score: float, trend_alignment: Dict) -> bool:
        """Detect if trading against the main trend"""
        return (signal_score > 0 and trend_alignment['primary_trend'] == 'down') or \
               (signal_score < 0 and trend_alignment['primary_trend'] == 'up')