import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from scipy.optimize import minimize
from scipy.stats import norm

class PortfolioAnalyzer:
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily returns from price data"""
        return prices.pct_change().dropna()
    
    def calculate_portfolio_metrics(self, weights: np.ndarray, returns: pd.DataFrame) -> Dict:
        """Calculate portfolio metrics including expected return, volatility, and Sharpe ratio"""
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
        metrics = self.calculate_portfolio_metrics(optimal_weights, returns)
        
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
        
        return results 