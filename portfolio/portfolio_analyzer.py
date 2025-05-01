import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from scipy.optimize import minimize
from scipy.stats import norm

class PortfolioAnalyzer:
    def __init__(self):
        self.positions: Dict[str, float] = {}  # symbol -> quantity
        self.prices: Dict[str, float] = {}     # symbol -> current_price
        self.historical_data: Dict[str, pd.DataFrame] = {}  # symbol -> historical price data
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def add_position(self, symbol: str, quantity: float, price: float):
        """Add or update a position in the portfolio."""
        self.positions[symbol] = quantity
        self.prices[symbol] = price

    def remove_position(self, symbol: str):
        """Remove a position from the portfolio."""
        if symbol in self.positions:
            del self.positions[symbol]
        if symbol in self.prices:
            del self.prices[symbol]

    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value."""
        return sum(self.positions[symbol] * self.prices[symbol] 
                  for symbol in self.positions)

    def get_position_weights(self) -> Dict[str, float]:
        """Calculate position weights in the portfolio."""
        total_value = self.get_portfolio_value()
        if total_value == 0:
            return {symbol: 0 for symbol in self.positions}
        
        return {
            symbol: (self.positions[symbol] * self.prices[symbol] / total_value)
            for symbol in self.positions
        }

    def calculate_returns(self) -> Dict[str, float]:
        """Calculate returns for each position."""
        returns = {}
        for symbol in self.positions:
            if symbol in self.historical_data:
                hist_data = self.historical_data[symbol]
                if not hist_data.empty:
                    initial_price = hist_data.iloc[0]['close']
                    current_price = self.prices[symbol]
                    returns[symbol] = (current_price - initial_price) / initial_price
        return returns

    def calculate_portfolio_metrics(self) -> Dict[str, float]:
        """Calculate basic portfolio metrics."""
        portfolio_value = self.get_portfolio_value()
        weights = self.get_position_weights()
        returns = self.calculate_returns()
        
        # Calculate portfolio return
        portfolio_return = sum(weights.get(symbol, 0) * returns.get(symbol, 0) 
                             for symbol in self.positions)

        # Calculate other metrics
        metrics = {
            'total_value': portfolio_value,
            'return': portfolio_return,
            'position_count': len(self.positions),
            'timestamp': datetime.now().isoformat()
        }

        return metrics

    def update_prices(self, new_prices: Dict[str, float]):
        """Update current prices for positions."""
        for symbol, price in new_prices.items():
            if symbol in self.positions:
                self.prices[symbol] = price

    def update_historical_data(self, symbol: str, data: pd.DataFrame):
        """Update historical data for a symbol."""
        self.historical_data[symbol] = data

    def get_portfolio_summary(self) -> Dict:
        """Get a complete portfolio summary."""
        metrics = self.calculate_portfolio_metrics()
        weights = self.get_position_weights()
        returns = self.calculate_returns()

        positions_summary = []
        for symbol in self.positions:
            positions_summary.append({
                'symbol': symbol,
                'quantity': self.positions[symbol],
                'price': self.prices[symbol],
                'value': self.positions[symbol] * self.prices[symbol],
                'weight': weights.get(symbol, 0),
                'return': returns.get(symbol, 0)
            })

        return {
            'metrics': metrics,
            'positions': positions_summary
        }

    def calculate_optimization_metrics(self, weights: np.ndarray, returns: pd.DataFrame) -> Dict:
        """Calculate advanced portfolio metrics for optimization including expected return, volatility, and Sharpe ratio"""
        portfolio_return = np.sum(returns.mean() * weights) * 252  # Annualized
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio
        }
    
    def calculate_var(self, returns: pd.DataFrame, weights: np.ndarray, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk (VaR) for the portfolio"""
        portfolio_returns = np.dot(returns, weights)
        var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
        return var
    
    def optimize_portfolio(self, returns: pd.DataFrame, target_return: float = None) -> Tuple[np.ndarray, Dict]:
        """Optimize portfolio weights using Markowitz optimization"""
        n_assets = len(returns.columns)
        
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
            {'type': 'ineq', 'fun': lambda x: x}  # Weights are positive
        ]
        
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: np.sum(returns.mean() * x) * 252 - target_return
            })
        
        initial_weights = np.ones(n_assets) / n_assets
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        metrics = self.calculate_optimization_metrics(optimal_weights, returns)
        
        return optimal_weights, metrics
    
    def analyze_sector_exposure(self, portfolio: Dict[str, float], sector_data: Dict[str, str]) -> Dict[str, float]:
        """Analyze portfolio exposure across different sectors"""
        sector_exposure = {}
        for symbol, weight in portfolio.items():
            sector = sector_data.get(symbol, 'Unknown')
            sector_exposure[sector] = sector_exposure.get(sector, 0) + weight
        return sector_exposure
    
    def stress_test_portfolio(self, returns: pd.DataFrame, weights: np.ndarray, 
                            scenarios: List[Dict[str, float]]) -> Dict[str, float]:
        """Perform stress testing on portfolio under different market scenarios"""
        results = {}
        for scenario in scenarios:
            adjusted_returns = returns.copy()
            for symbol, impact in scenario.items():
                if symbol in returns.columns:
                    adjusted_returns[symbol] = returns[symbol] * (1 + impact)
            
            portfolio_return = np.sum(adjusted_returns.mean() * weights) * 252
            results[str(scenario)] = portfolio_return

