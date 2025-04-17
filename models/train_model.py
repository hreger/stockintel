import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from price_predictor import PricePredictor
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def train_and_evaluate(symbols: list, sequence_length: int = 60, epochs: int = 50):
    """Train and evaluate models for multiple symbols"""
    predictor = PricePredictor(sequence_length=sequence_length)
    results = []
    
    for symbol in symbols:
        print(f"\nTraining model for {symbol}...")
        try:
            # Train the model
            metrics = predictor.train(symbol, epochs=epochs)
            print(f"Training completed for {symbol}")
            print(f"Train Loss: {metrics['train_loss']:.4f}")
            print(f"Validation Loss: {metrics['val_loss']:.4f}")
            print(f"Data Points Used: {metrics['data_points']}")
            
            # Make predictions
            predictions = predictor.predict(symbol, days=5)
            
            # Plot predictions
            plt.figure(figsize=(12, 6))
            plt.plot(predictions['date'], predictions['predicted_price'], 'r-', label='Predicted')
            plt.title(f'{symbol} Price Predictions')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.legend()
            plt.grid(True)
            plt.savefig(f'models/predictions/{symbol}_predictions.png')
            plt.close()
            
            results.append({
                'symbol': symbol,
                'train_loss': metrics['train_loss'],
                'val_loss': metrics['val_loss'],
                'data_points': metrics['data_points']
            })
            
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            continue
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv('models/training_results.csv', index=False)
    print("\nTraining results saved to 'models/training_results.csv'")

if __name__ == "__main__":
    # Create necessary directories
    import os
    os.makedirs('models/predictions', exist_ok=True)
    os.makedirs('models/saved_models', exist_ok=True)
    
    # Symbols to train
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    # Train and evaluate models
    train_and_evaluate(symbols, sequence_length=60, epochs=50) 