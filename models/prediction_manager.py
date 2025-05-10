from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import joblib
from datetime import datetime, timedelta

class PredictionManager:
    def __init__(self):
        self.models = {}
        self.model_metrics = {}
        self.last_training_date = {}
        self.retraining_interval = timedelta(days=30)  # Retrain monthly
        
    def prepare_data(self, data: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepare data with proper time series splitting
        """
        # Sort by date to respect time series nature
        data = data.sort_index()
        
        # Create features without looking ahead
        features = self._create_features(data)
        
        # Time-based train/test split
        train_size = int(len(data) * 0.8)
        train_data = features.iloc[:train_size]
        test_data = features.iloc[train_size:]
        
        return train_data, test_data
        
    def _create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create features without future data leakage
        """
        features = pd.DataFrame()
        
        # Use only past data for feature creation
        features['returns'] = data['close'].pct_change()
        features['volatility'] = features['returns'].rolling(20).std()
        features['ma_50'] = data['close'].rolling(50).mean()
        features['ma_200'] = data['close'].rolling(200).mean()
        
        # Remove rows with NaN values from lookback periods
        features = features.dropna()
        
        return features
        
    def train_models(self, train_data: pd.DataFrame, target_col: str):
        """
        Train ensemble of models with cross-validation
        """
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        models = {
            'rf': RandomForestRegressor(n_estimators=100),
            'gb': GradientBoostingRegressor(n_estimators=100)
        }
        
        for name, model in models.items():
            cv_scores = []
            
            for train_idx, val_idx in tscv.split(train_data):
                X_train = train_data.iloc[train_idx].drop(target_col, axis=1)
                y_train = train_data.iloc[train_idx][target_col]
                X_val = train_data.iloc[val_idx].drop(target_col, axis=1)
                y_val = train_data.iloc[val_idx][target_col]
                
                # Train model
                model.fit(X_train, y_train)
                
                # Validate
                predictions = model.predict(X_val)
                mape = mean_absolute_percentage_error(y_val, predictions)
                cv_scores.append(mape)
            
            self.models[name] = model
            self.model_metrics[name] = {
                'cv_mape': np.mean(cv_scores),
                'cv_std': np.std(cv_scores)
            }
            
        self.last_training_date = datetime.now()
        
    def get_ensemble_prediction(self, features: pd.DataFrame) -> Dict:
        """
        Get weighted prediction from ensemble
        """
        predictions = {}
        weights = {}
        
        # Check if retraining is needed
        if datetime.now() - self.last_training_date > self.retraining_interval:
            return {
                'error': 'Models need retraining',
                'last_training': self.last_training_date
            }
        
        # Get predictions from each model
        for name, model in self.models.items():
            predictions[name] = model.predict(features)
            # Weight based on CV performance
            weights[name] = 1 / self.model_metrics[name]['cv_mape']
            
        # Weighted ensemble prediction
        total_weight = sum(weights.values())
        ensemble_pred = sum(pred * weights[name] / total_weight 
                          for name, pred in predictions.items())
        
        return {
            'prediction': ensemble_pred,
            'model_contributions': {
                name: weight / total_weight 
                for name, weight in weights.items()
            },
            'metrics': self.model_metrics,
            'limitations': self._get_model_limitations()
        }
        
    def _get_model_limitations(self) -> List[str]:
        """
        Document model limitations
        """
        return [
            "Models assume market conditions similar to training data",
            "Predictions may be less accurate during market regime changes",
            "Limited ability to predict black swan events",
            "Performance varies by market volatility",
            f"Models trained on data up to {self.last_training_date}",
            "Past performance does not guarantee future results"
        ]