import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    COMBINED = "combined"

@dataclass
class TradingSignal:
    symbol: str
    signal_type: SignalType
    strength: float
    confidence: float
    timestamp: datetime
    details: Dict

class MarketScanner:
    def __init__(self):
        self.technical_indicators = {
            'rsi': self._calculate_rsi,
            'macd': self._calculate_macd,
            'bollinger_bands': self._calculate_bollinger_bands
        }
        
        self.fundamental_metrics = {
            'pe_ratio': self._analyze_pe_ratio,
            'debt_to_equity': self._analyze_debt_to_equity,
            'profit_margin': self._analyze_profit_margin
        }
    
    def scan_market(self, 
                   data: Dict[str, pd.DataFrame],
                   criteria: Dict) -> List[TradingSignal]:
        """Scan market for trading opportunities"""
        signals = []
        
        for symbol, df in data.items():
            # Technical analysis
            technical_signals = self._scan_technical(df, criteria.get('technical', {}))
            signals.extend(technical_signals)
            
            # Fundamental analysis
            fundamental_signals = self._scan_fundamental(df, criteria.get('fundamental', {}))
            signals.extend(fundamental_signals)
            
            # Combined analysis
            combined_signals = self._combine_signals(technical_signals, fundamental_signals)
            signals.extend(combined_signals)
        
        return signals
    
    def _scan_technical(self, 
                       data: pd.DataFrame,
                       criteria: Dict) -> List[TradingSignal]:
        """Scan for technical trading signals"""
        signals = []
        
        for indicator, params in criteria.items():
            if indicator in self.technical_indicators:
                indicator_func = self.technical_indicators[indicator]
                signal = indicator_func(data, **params)
                
                if signal is not None:
                    signals.append(TradingSignal(
                        symbol=data.name,
                        signal_type=SignalType.TECHNICAL,
                        strength=signal['strength'],
                        confidence=signal['confidence'],
                        timestamp=datetime.now(),
                        details={
                            'indicator': indicator,
                            'value': signal['value'],
                            'threshold': params.get('threshold')
                        }
                    ))
        
        return signals
    
    def _scan_fundamental(self,
                         data: pd.DataFrame,
                         criteria: Dict) -> List[TradingSignal]:
        """Scan for fundamental trading signals"""
        signals = []
        
        for metric, params in criteria.items():
            if metric in self.fundamental_metrics:
                metric_func = self.fundamental_metrics[metric]
                signal = metric_func(data, **params)
                
                if signal is not None:
                    signals.append(TradingSignal(
                        symbol=data.name,
                        signal_type=SignalType.FUNDAMENTAL,
                        strength=signal['strength'],
                        confidence=signal['confidence'],
                        timestamp=datetime.now(),
                        details={
                            'metric': metric,
                            'value': signal['value'],
                            'threshold': params.get('threshold')
                        }
                    ))
        
        return signals
    
    def _combine_signals(self,
                        technical_signals: List[TradingSignal],
                        fundamental_signals: List[TradingSignal]) -> List[TradingSignal]:
        """Combine technical and fundamental signals"""
        combined_signals = []
        
        # Group signals by symbol
        all_signals = technical_signals + fundamental_signals
        signal_groups = {}
        for signal in all_signals:
            if signal.symbol not in signal_groups:
                signal_groups[signal.symbol] = []
            signal_groups[signal.symbol].append(signal)
        
        # Create combined signals
        for symbol, signals in signal_groups.items():
            if len(signals) >= 2:  # Need at least 2 signals to combine
                strength = np.mean([s.strength for s in signals])
                confidence = np.mean([s.confidence for s in signals])
                
                combined_signals.append(TradingSignal(
                    symbol=symbol,
                    signal_type=SignalType.COMBINED,
                    strength=strength,
                    confidence=confidence,
                    timestamp=datetime.now(),
                    details={
                        'component_signals': [
                            {
                                'type': s.signal_type.value,
                                'strength': s.strength,
                                'confidence': s.confidence
                            } for s in signals
                        ]
                    }
                ))
        
        return combined_signals
    
    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14, 
                      overbought: float = 70, oversold: float = 30) -> Dict:
        """Calculate RSI and generate signal"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        if current_rsi > overbought:
            return {
                'strength': (current_rsi - overbought) / (100 - overbought),
                'confidence': 0.8,
                'value': current_rsi
            }
        elif current_rsi < oversold:
            return {
                'strength': (oversold - current_rsi) / oversold,
                'confidence': 0.8,
                'value': current_rsi
            }
        return None
    
    def _calculate_macd(self, data: pd.DataFrame,
                       fast_period: int = 12,
                       slow_period: int = 26,
                       signal_period: int = 9) -> Dict:
        """Calculate MACD and generate signal"""
        exp1 = data['close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = data['close'].ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        
        if current_macd > current_signal:
            return {
                'strength': (current_macd - current_signal) / abs(current_signal),
                'confidence': 0.7,
                'value': current_macd
            }
        elif current_macd < current_signal:
            return {
                'strength': (current_signal - current_macd) / abs(current_signal),
                'confidence': 0.7,
                'value': current_macd
            }
        return None
    
    def _calculate_bollinger_bands(self, data: pd.DataFrame,
                                 period: int = 20,
                                 std_dev: float = 2) -> Dict:
        """Calculate Bollinger Bands and generate signal"""
        sma = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        current_price = data['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        
        if current_price > current_upper:
            return {
                'strength': (current_price - current_upper) / current_upper,
                'confidence': 0.75,
                'value': current_price
            }
        elif current_price < current_lower:
            return {
                'strength': (current_lower - current_price) / current_lower,
                'confidence': 0.75,
                'value': current_price
            }
        return None
    
    def _analyze_pe_ratio(self, data: pd.DataFrame,
                         threshold: float = 20) -> Dict:
        """Analyze P/E ratio and generate signal"""
        pe_ratio = data['pe_ratio'].iloc[-1]
        
        if pe_ratio < threshold:
            return {
                'strength': (threshold - pe_ratio) / threshold,
                'confidence': 0.6,
                'value': pe_ratio
            }
        return None
    
    def _analyze_debt_to_equity(self, data: pd.DataFrame,
                              threshold: float = 1.0) -> Dict:
        """Analyze debt-to-equity ratio and generate signal"""
        d_to_e = data['debt_to_equity'].iloc[-1]
        
        if d_to_e < threshold:
            return {
                'strength': (threshold - d_to_e) / threshold,
                'confidence': 0.65,
                'value': d_to_e
            }
        return None
    
    def _analyze_profit_margin(self, data: pd.DataFrame,
                             threshold: float = 0.1) -> Dict:
        """Analyze profit margin and generate signal"""
        profit_margin = data['profit_margin'].iloc[-1]
        
        if profit_margin > threshold:
            return {
                'strength': (profit_margin - threshold) / (1 - threshold),
                'confidence': 0.7,
                'value': profit_margin
            }
        return None 