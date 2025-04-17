import pandas as pd
import numpy as np
from typing import Dict, List, Callable
from datetime import datetime, timedelta

class StrategyTester:
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.commission_rate = 0.001  # 0.1% commission per trade
    
    def run_backtest(self, 
                    data: pd.DataFrame,
                    strategy: Callable,
                    parameters: Dict = None) -> Dict:
        """Run backtest on historical data"""
        if parameters is None:
            parameters = {}
        
        # Initialize portfolio
        portfolio = {
            'cash': self.initial_capital,
            'positions': {},
            'trades': [],
            'equity': [self.initial_capital]
        }
        
        # Run strategy on each day
        for i in range(len(data)):
            current_data = data.iloc[i]
            signal = strategy(current_data, **parameters)
            
            # Execute trades based on signal
            self._execute_trades(signal, current_data, portfolio)
            
            # Update portfolio value
            portfolio_value = self._calculate_portfolio_value(portfolio, current_data)
            portfolio['equity'].append(portfolio_value)
        
        # Calculate performance metrics
        returns = pd.Series(portfolio['equity']).pct_change().dropna()
        metrics = self._calculate_metrics(returns)
        
        return {
            'portfolio': portfolio,
            'metrics': metrics,
            'returns': returns
        }
    
    def _execute_trades(self, signal: int, data: pd.Series, portfolio: Dict):
        """Execute trades based on signal (-1: sell, 0: hold, 1: buy)"""
        symbol = data.name
        price = data['close']
        
        if signal == 1 and symbol not in portfolio['positions']:
            # Buy
            shares = (portfolio['cash'] * 0.95) / price  # Use 95% of cash
            cost = shares * price * (1 + self.commission_rate)
            
            if cost <= portfolio['cash']:
                portfolio['cash'] -= cost
                portfolio['positions'][symbol] = shares
                portfolio['trades'].append({
                    'date': data.name,
                    'type': 'buy',
                    'symbol': symbol,
                    'shares': shares,
                    'price': price
                })
        
        elif signal == -1 and symbol in portfolio['positions']:
            # Sell
            shares = portfolio['positions'][symbol]
            proceeds = shares * price * (1 - self.commission_rate)
            
            portfolio['cash'] += proceeds
            del portfolio['positions'][symbol]
            portfolio['trades'].append({
                'date': data.name,
                'type': 'sell',
                'symbol': symbol,
                'shares': shares,
                'price': price
            })
    
    def _calculate_portfolio_value(self, portfolio: Dict, current_data: pd.Series) -> float:
        """Calculate current portfolio value"""
        positions_value = sum(
            shares * current_data['close']
            for symbol, shares in portfolio['positions'].items()
        )
        return portfolio['cash'] + positions_value
    
    def _calculate_metrics(self, returns: pd.Series) -> Dict:
        """Calculate performance metrics"""
        total_return = (returns + 1).prod() - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        annual_volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility if annual_volatility != 0 else 0
        
        # Calculate maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns / rolling_max - 1
        max_drawdown = drawdowns.min()
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }
    
    def optimize_parameters(self,
                          data: pd.DataFrame,
                          strategy: Callable,
                          parameter_grid: Dict[str, List]) -> Dict:
        """Optimize strategy parameters using grid search"""
        best_metrics = None
        best_parameters = None
        
        # Generate all parameter combinations
        from itertools import product
        param_names = list(parameter_grid.keys())
        param_values = list(parameter_grid.values())
        
        for params in product(*param_values):
            parameters = dict(zip(param_names, params))
            
            # Run backtest
            results = self.run_backtest(data, strategy, parameters)
            metrics = results['metrics']
            
            # Use Sharpe ratio as optimization criterion
            if best_metrics is None or metrics['sharpe_ratio'] > best_metrics['sharpe_ratio']:
                best_metrics = metrics
                best_parameters = parameters
        
        return {
            'best_parameters': best_parameters,
            'best_metrics': best_metrics
        } 