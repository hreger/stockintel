import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class ARIMAPredictor:
    def __init__(self, order=(5,1,0)):
        self.order = order
        self.model = None
        self.history = None
        
    def prepare_data(self, data):
        """Prepare time series data for ARIMA model"""
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df['price']
    
    def fit(self, data):
        """Fit ARIMA model to historical data"""
        self.history = self.prepare_data(data)
        self.model = ARIMA(self.history, order=self.order)
        self.model = self.model.fit()
        return self
    
    def predict(self, steps=7):
        """Make predictions for the next n days"""
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        forecast = self.model.forecast(steps=steps)
        return forecast
    
    def evaluate(self, test_data):
        """Evaluate model performance on test data"""
        test_series = self.prepare_data(test_data)
        predictions = self.predict(steps=len(test_series))
        mae = mean_absolute_error(test_series, predictions)
        return {
            'mae': mae,
            'predictions': predictions.tolist(),
            'actual': test_series.tolist()
        }
    
    def update(self, new_data):
        """Update model with new data points"""
        new_series = self.prepare_data(new_data)
        self.history = pd.concat([self.history, new_series])
        self.model = ARIMA(self.history, order=self.order)
        self.model = self.model.fit()
        return self 