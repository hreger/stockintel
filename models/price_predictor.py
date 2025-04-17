import numpy as np
import pandas as pd
from typing import Tuple, Dict
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy.orm import Session
from data_ingestion.database import StockData, get_db
import joblib
import os



class PricePredictor:
    def __init__(self, sequence_length: int = 60):
        self.sequence_length = sequence_length
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        
    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for LSTM model"""
        # Scale the data
        scaled_data = self.scaler.fit_transform(data[['price']].values)
        
        # Create sequences
        X, y = [], []
        for i in range(len(scaled_data) - self.sequence_length):
            X.append(scaled_data[i:(i + self.sequence_length)])
            y.append(scaled_data[i + self.sequence_length])
            
        return np.array(X), np.array(y)
    
    def build_model(self):
        """Build LSTM model"""
        self.model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self.sequence_length, 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        self.model.compile(optimizer='adam', loss='mean_squared_error')
    
    def train(self, symbol: str, epochs: int = 50, batch_size: int = 32) -> Dict:
        """Train the model for a specific symbol"""
        # Get data from database
        db = next(get_db())
        try:
            data = pd.read_sql(
                db.query(StockData)
                .filter(StockData.symbol == symbol)
                .order_by(StockData.timestamp)
                .statement,
                db.bind
            )
            
            if len(data) < self.sequence_length * 2:
                raise ValueError(f"Not enough data for {symbol}")
            
            # Prepare data
            X, y = self.prepare_data(data)
            
            # Split into train and test
            train_size = int(len(X) * 0.8)
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
            # Build and train model
            self.build_model()
            history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(X_test, y_test),
                verbose=1
            )
            
            # Save model and scaler
            self._save_model(symbol)
            
            return {
                'train_loss': history.history['loss'][-1],
                'val_loss': history.history['val_loss'][-1],
                'data_points': len(data)
            }
            
        finally:
            db.close()
    
    def predict(self, symbol: str, days: int = 5) -> pd.DataFrame:
        """Make predictions for a symbol"""
        # Load model and scaler
        self._load_model(symbol)
        
        # Get recent data
        db = next(get_db())
        try:
            recent_data = pd.read_sql(
                db.query(StockData)
                .filter(StockData.symbol == symbol)
                .order_by(StockData.timestamp.desc())
                .limit(self.sequence_length)
                .statement,
                db.bind
            )
            
            if len(recent_data) < self.sequence_length:
                raise ValueError(f"Not enough recent data for {symbol}")
            
            # Prepare data for prediction
            scaled_data = self.scaler.transform(recent_data[['price']].values)
            X = np.array([scaled_data])
            
            # Make predictions
            predictions = []
            current_sequence = X[0]
            
            for _ in range(days):
                pred = self.model.predict(current_sequence.reshape(1, self.sequence_length, 1))
                predictions.append(pred[0][0])
                current_sequence = np.append(current_sequence[1:], pred)
            
            # Inverse transform predictions
            predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
            
            # Create prediction dates
            last_date = recent_data['timestamp'].iloc[0]
            dates = pd.date_range(start=last_date, periods=days+1, freq='D')[1:]
            
            return pd.DataFrame({
                'date': dates,
                'predicted_price': predictions.flatten()
            })
            
        finally:
            db.close()
    
    def _save_model(self, symbol: str):
        """Save model and scaler for a symbol"""
        os.makedirs('models/saved_models', exist_ok=True)
        self.model.save(f'models/saved_models/{symbol}_model.h5')
        joblib.dump(self.scaler, f'models/saved_models/{symbol}_scaler.pkl')
    
    def _load_model(self, symbol: str):
        """Load model and scaler for a symbol"""
        self.model = tf.keras.models.load_model(f'models/saved_models/{symbol}_model.h5')
        self.scaler = joblib.load(f'models/saved_models/{symbol}_scaler.pkl') 