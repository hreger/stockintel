import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List
from portfolio.portfolio_analyzer import PortfolioAnalyzer

class PortfolioDashboard:
    def __init__(self):
        self.analyzer = PortfolioAnalyzer()
    
    def create_portfolio_performance_chart(self, historical_prices: pd.DataFrame, 
                                         weights: Dict[str, float]) -> go.Figure:
        """Create a chart showing portfolio performance over time"""
        returns = self.analyzer.calculate_returns(historical_prices)
        portfolio_returns = pd.Series(np.dot(returns, list(weights.values())), 
                                    index=returns.index)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cumulative_returns.index,
            y=cumulative_returns.values,
            mode='lines',
            name='Portfolio Value'
        ))
        
        fig.update_layout(
            title='Portfolio Performance Over Time',
            xaxis_title='Date',
            yaxis_title='Cumulative Return',
            template='plotly_dark'
        )
        
        return fig
    
    def create_risk_metrics_chart(self, returns: pd.DataFrame, 
                                weights: Dict[str, float]) -> go.Figure:
        """Create a chart showing portfolio risk metrics"""
        metrics = self.analyzer.calculate_portfolio_metrics(
            np.array(list(weights.values())), 
            returns
        )
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(metrics.keys()),
                y=list(metrics.values()),
                text=[f'{v:.2%}' if k != 'sharpe_ratio' else f'{v:.2f}' 
                      for k, v in metrics.items()],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title='Portfolio Risk Metrics',
            template='plotly_dark'
        )
        
        return fig
    
    def create_sector_exposure_chart(self, portfolio: Dict[str, float], 
                                   sector_data: Dict[str, str]) -> go.Figure:
        """Create a pie chart showing sector exposure"""
        sector_exposure = self.analyzer.analyze_sector_exposure(portfolio, sector_data)
        
        fig = go.Figure(data=[go.Pie(
            labels=list(sector_exposure.keys()),
            values=list(sector_exposure.values()),
            textinfo='label+percent',
            hole=.3
        )])
        
        fig.update_layout(
            title='Portfolio Sector Exposure',
            template='plotly_dark'
        )
        
        return fig
    
    def create_efficient_frontier(self, returns: pd.DataFrame) -> go.Figure:
        """Create a chart showing the efficient frontier"""
        target_returns = np.linspace(returns.mean().min() * 252, 
                                   returns.mean().max() * 252, 20)
        volatilities = []
        
        for target in target_returns:
            weights, metrics = self.analyzer.optimize_portfolio(returns, target)
            volatilities.append(metrics['volatility'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=volatilities,
            y=target_returns,
            mode='lines',
            name='Efficient Frontier'
        ))
        
        fig.update_layout(
            title='Efficient Frontier',
            xaxis_title='Volatility',
            yaxis_title='Expected Return',
            template='plotly_dark'
        )
        
        return fig
    
    def create_stress_test_chart(self, returns: pd.DataFrame, 
                               weights: Dict[str, float],
                               scenarios: List[Dict[str, float]]) -> go.Figure:
        """Create a chart showing stress test results"""
        results = self.analyzer.stress_test_portfolio(
            returns, 
            np.array(list(weights.values())),
            scenarios
        )
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(results.keys()),
                y=list(results.values()),
                text=[f'{v:.2%}' for v in results.values()],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title='Portfolio Stress Test Results',
            xaxis_title='Scenario',
            yaxis_title='Expected Return',
            template='plotly_dark'
        )
        
        return fig 