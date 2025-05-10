import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error

class BaselineModels:
    def __init__(self):
        self.models = {}
        
    def train_naive_model(self, data: pd.DataFrame, target_col: str = 'close'):
        """Train a naive model that predicts tomorrow = today"""
        # This is just for baseline comparison
        self.models['naive'] = {
            'type': 'naive',
            'prediction': lambda x: x[target_col].iloc[-1]
        }
        
        # Evaluate
        y_true = data[target_col].iloc[1:].values
        y_pred = data[target_col].iloc[:-1].values
        mape = mean_absolute_percentage_error(y_true, y_pred)
        
        return {
            'model': 'naive',
            'mape': mape,
            'description': 'Predicts that tomorrow equals today'
        }
        
    def train_linear_model(self, data: pd.DataFrame, target_col: str = 'close', window: int = 5):
        """Train a simple linear regression model"""
        # Create features (last n days)
        X = []
        y = []
        
        for i in range(len(data) - window):
            X.append(data[target_col].iloc[i:i+window].values)
            y.append(data[target_col].iloc[i+window])
            
        X = np.array(X)
        y = np.array(y)
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Save model
        self.models['linear'] = {
            'type': 'linear',
            'model': model,
            'window': window
        }
        
        # Evaluate
        y_pred = model.predict(X)
        mape = mean_absolute_percentage_error(y, y_pred)
        
        return {
            'model': 'linear',
            'mape': mape,
            'description': f'Linear regression using last {window} days'
        }