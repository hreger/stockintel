from flask import Flask, render_template, request, jsonify, redirect, url_for
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime, timedelta
import os
import secrets

from data_ingestion.api_client import StockDataClient
from portfolio.portfolio_analyzer import PortfolioAnalyzer
from dashboard.components.technical_indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key

# Initialize components
stock_client = StockDataClient()
portfolio_analyzer = PortfolioAnalyzer()

# Initialize sample portfolio data
portfolio_analyzer.add_position('AAPL', 100, 150.0)
portfolio_analyzer.add_position('MSFT', 50, 300.0)
portfolio_analyzer.add_position('GOOGL', 30, 2800.0)
portfolio_analyzer.add_position('AMZN', 20, 3200.0)
portfolio_analyzer.add_position('TSLA', 40, 800.0)

# Default symbol
DEFAULT_SYMBOL = 'AAPL'

# Market indices data (sample)
market_indices = {
    'S&P 500': {'value': '4,567.31', 'change': '+0.65%', 'color': 'green'},
    'NASDAQ': {'value': '15,982.62', 'change': '+1.17%', 'color': 'green'},
    'DOW': {'value': '36,804.47', 'change': '+0.19%', 'color': 'green'},
    'RUSSELL': {'value': '2,292.88', 'change': '-0.25%', 'color': 'red'},
    'VIX': {'value': '15.42', 'change': '-0.05%', 'color': 'red'}
}

# Market signals (sample)
market_signals = [
    {'symbol': 'AAPL', 'message': 'volume crosses last session', 'time': '2 hours ago', 'details': 'AAPL has 100 shares traded which are above 50 traded in the previous session'},
    {'symbol': 'MSFT', 'message': 'has recorded trading volume of 150K', 'time': '3 hours ago', 'details': 'MSFT has 150 shares traded which are above 120 traded in the previous session'},
    {'symbol': 'GOOGL', 'message': 'volume crosses last session', 'time': '4 hours ago', 'details': 'GOOGL has 80 shares traded which are above 70 traded in the previous session'},
    {'symbol': 'AMZN', 'message': 'has risen by 7.50%', 'time': '2 hours ago', 'details': 'AMZN is trading PKR 3.75 up its last close PKR 53.74 (+7.50%)'},
    {'symbol': 'TSLA', 'message': 'volume crosses last session', 'time': '1 hour ago', 'details': 'TSLA has 15 shares traded which are above 500 traded in the previous session'}
]

# Top performers (sample)
top_performers = [
    {'symbol': 'AAPL', 'price': '180.95', 'change': '+2.3%'},
    {'symbol': 'MSFT', 'price': '325.42', 'change': '+1.8%'},
    {'symbol': 'GOOGL', 'price': '2950.12', 'change': '+1.5%'},
    {'symbol': 'AMZN', 'price': '3450.00', 'change': '+3.2%'},
    {'symbol': 'TSLA', 'price': '850.75', 'change': '+4.1%'}
]

# News and announcements (sample)
news_items = [
    {'title': 'Market Update', 'description': 'S&P 500 reaches new all-time high', 'time': '1 hour ago'},
    {'title': 'Economic Data', 'description': 'Unemployment rate falls to 3.8%', 'time': '3 hours ago'},
    {'title': 'Fed Announcement', 'description': 'Interest rates remain unchanged', 'time': '5 hours ago'}
]

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string for HTML display"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='#1a1a1a')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

def prepare_stock_data(symbol, timeframe="1D"):
    """Fetch and prepare stock data for visualization"""
    try:
        # Fetch data from Alpha Vantage
        data = stock_client.get_daily_time_series(symbol, outputsize="compact")
        
        # Extract time series data
        time_series = data.get('Time Series (Daily)', {})
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        
        # Convert string values to float
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
            
        # Rename columns
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        
        # Sort by date
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Filter based on timeframe
        if timeframe == "1D":
            df = df.iloc[-1:]
        elif timeframe == "1W":
            df = df.iloc[-5:]
        elif timeframe == "1M":
            df = df.iloc[-21:]
        elif timeframe == "3M":
            df = df.iloc[-63:]
        elif timeframe == "6M":
            df = df.iloc[-126:]
        elif timeframe == "1Y":
            df = df.iloc[-252:]
        
        return df
    except Exception as e:
        print(f"Error preparing stock data: {e}")
        return pd.DataFrame()

def create_price_chart(df, symbol):
    """Create price chart with Matplotlib"""
    if df.empty:
        return None
    
    # Set the style to dark background
    plt.style.use('dark_background')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    # Plot the close price
    ax.plot(df.index, df['close'], color='#00ff00', linewidth=2)
    
    # Add Bollinger Bands
    upper, middle, lower = calculate_bollinger_bands(df['close'])
    ax.plot(df.index, upper, 'r--', linewidth=1, alpha=0.7)
    ax.plot(df.index, middle, color='#4287f5', linewidth=1, alpha=0.7)
    ax.plot(df.index, lower, 'r--', linewidth=1, alpha=0.7)
    
    # Add volume as bars at the bottom
    volume_ax = ax.twinx()
    volume_ax.set_ylim(0, df['volume'].max() * 3)
    volume_ax.bar(df.index, df['volume'], color='#4287f5', alpha=0.3, width=0.8)
    volume_ax.set_ylabel('Volume', color='#4287f5')
    volume_ax.tick_params(axis='y', colors='#4287f5')
    volume_ax.spines['right'].set_color('#4287f5')
    
    # Set title and labels
    ax.set_title(f'{symbol} Price Chart', color='white', fontsize=14)
    ax.set_xlabel('Date', color='white')
    ax.set_ylabel('Price ($)', color='white')
    
    # Style the grid
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Style the ticks
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    
    # Style the spines
    for spine in ax.spines.values():
        spine.set_color('#333333')
    
    return fig

def create_technical_indicators_chart(df, symbol):
    """Create a chart with RSI and MACD"""
    if df.empty:
        return None
    
    # Set the style to dark background
    plt.style.use('dark_background')
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={'height_ratios': [1, 1]})
    fig.patch.set_facecolor('#1a1a1a')
    
    # RSI Plot
    ax1.set_facecolor('#1a1a1a')
    rsi = calculate_rsi(df['close'])
    ax1.plot(df.index, rsi, color='purple', linewidth=2)
    ax1.axhline(y=70, color='red', linestyle='--', alpha=0.5)
    ax1.axhline(y=30, color='green', linestyle='--', alpha=0.5)
    ax1.set_title('RSI', color='white')
    ax1.set_ylim(0, 100)
    ax1.tick_params(axis='x', colors='white')
    ax1.tick_params(axis='y', colors='white')
    ax1.grid(True, linestyle='--', alpha=0.3)
    
    # MACD Plot
    ax2.set_facecolor('#1a1a1a')
    macd_line, signal_line, histogram = calculate_macd(df['close'])
    ax2.plot(df.index, macd_line, color='#00BFFF', linewidth=2, label='MACD')
    ax2.plot(df.index, signal_line, color='#FF6347', linewidth=2, label='Signal')
    
    # Plot histogram as bar chart
    for i, value in enumerate(histogram):
        color = 'green' if value >= 0 else 'red'
        ax2.bar(df.index[i], value, color=color, width=1, alpha=0.5)
    
    ax2.set_title('MACD', color='white')
    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')
    ax2.grid(True, linestyle='--', alpha=0.3)
    ax2.legend(loc='upper left')
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

def create_portfolio_pie_chart():
    """Create portfolio distribution pie chart"""
    summary = portfolio_analyzer.get_portfolio_summary()
    positions = pd.DataFrame(summary['positions'])
    
    # Set the style to dark background
    plt.style.use('dark_background')
    
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        positions['value'], 
        labels=positions['symbol'], 
        autopct='%1.1f%%',
        textprops={'color': 'white'},
        colors=plt.cm.tab10.colors,
        wedgeprops={'edgecolor': '#1a1a1a', 'linewidth': 1}
    )
    
    # Style the text
    for text in texts:
        text.set_color('white')
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title('Portfolio Distribution', color='white', fontsize=14)
    
    return fig

@app.route('/')
def index():
    """Render the main dashboard page"""
    symbol = request.args.get('symbol', DEFAULT_SYMBOL)
    timeframe = request.args.get('timeframe', '1D')
    
    # Get stock data
    df = prepare_stock_data(symbol, timeframe)
    
    # Create charts
    charts = {}
    if not df.empty:
        charts['price_chart'] = fig_to_base64(create_price_chart(df, symbol))
        charts['technical_chart'] = fig_to_base64(create_technical_indicators_chart(df, symbol))
    
    # Get portfolio data
    portfolio_summary = portfolio_analyzer.get_portfolio_summary()
    portfolio_chart = fig_to_base64(create_portfolio_pie_chart())
    
    # Prepare template data
    template_data = {
        'symbol': symbol,
        'timeframe': timeframe,
        'charts': charts,
        'portfolio': {
            'value': f"${portfolio_summary['metrics']['total_value']:,.2f}",
            'return': f"{portfolio_summary['metrics']['return']*100:.2f}%",
            'positions': portfolio_summary['positions'],
            'chart': portfolio_chart
        },
        'market_indices': market_indices,
        'market_signals': market_signals,
        'top_performers': top_performers,
        'news_items': news_items
    }
    
    return render_template('dashboard.html', **template_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login functionality"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (replace with proper auth)
        if username == 'admin' and password == 'password':
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True)