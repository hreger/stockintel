import pandas as pd
import numpy as np

def calculate_rsi(data: pd.DataFrame, periods: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    close_delta = data['close'].diff()
    
    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    
    # Calculate the EWMA
    ma_up = up.ewm(com=periods - 1, adjust=False).mean()
    ma_down = down.ewm(com=periods - 1, adjust=False).mean()
    
    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))
    
    return rsi

def calculate_macd(data: pd.DataFrame) -> tuple:
    """Calculate MACD (Moving Average Convergence Divergence)"""
    # Calculate the short term exponential moving average
    exp1 = data['close'].ewm(span=12, adjust=False).mean()
    # Calculate the long term exponential moving average
    exp2 = data['close'].ewm(span=26, adjust=False).mean()
    # Calculate MACD line
    macd = exp1 - exp2
    # Calculate the signal line
    signal = macd.ewm(span=9, adjust=False).mean()
    
    return macd, signal

def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20) -> tuple:
    """Calculate Bollinger Bands"""
    # Calculate rolling mean and standard deviation
    rolling_mean = data['close'].rolling(window=window).mean()
    rolling_std = data['close'].rolling(window=window).std()
    
    # Calculate upper and lower bands
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)
    
    return upper_band, rolling_mean, lower_band