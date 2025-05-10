from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
from datetime import datetime, timedelta
import os

from data_ingestion.api_client import StockDataClient
from portfolio.portfolio_analyzer import PortfolioAnalyzer
from dashboard.components.technical_indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands

app = Flask(__name__)
app.secret_key = "your-secret-key"  # For session management

# Initialize components
stock_client = StockDataClient()
portfolio_analyzer = PortfolioAnalyzer()

# Initialize sample portfolio data
portfolio_analyzer.add_position('AAPL', 100, 150.0)
portfolio_analyzer.add_position('MSFT', 50, 300.0)
portfolio_analyzer.add_position('GOOGL', 30, 2800.0)

# Default symbol
DEFAULT_SYMBOL = 'AAPL'

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string for HTML display"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

def prepare_stock_data(symbol, outputsize="compact"):
    """Fetch and prepare stock data for visualization"""
    try:
        # Fetch data from Alpha Vantage
        data = stock_client.get_daily_time_series(symbol, outputsize)
        
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
        
        return df
    except Exception as e:
        print(f"Error preparing stock data: {e}")
        return pd.DataFrame()

def create_price_chart(df):
    """Create price chart with Matplotlib"""
    if df.empty:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df.index, df['close'], label='Close Price')
    
    # Add Bollinger Bands
    upper, middle, lower = calculate_bollinger_bands(df['close'])
    ax.plot(df.index, upper, 'r--', label='Upper Band')
    ax.plot(df.index, middle, 'g--', label='Middle Band')
    ax.plot(df.index, lower, 'r--', label='Lower Band')
    
    ax.set_title('Stock Price with Bollinger Bands')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price ($)')
    ax.legend()
    ax.grid(True)
    
    return fig

def create_volume_chart(df):
    """Create volume chart with Matplotlib"""
    if df.empty:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.bar(df.index, df['volume'], color='blue', alpha=0.6)
    ax.set_title('Trading Volume')
    ax.set_xlabel('Date')
    ax.set_ylabel('Volume')
    ax.grid(True, axis='y')
    
    return fig

def create_rsi_chart(df):
    """Create RSI chart with Matplotlib"""
    if df.empty:
        return None
    
    rsi = calculate_rsi(df['close'])
    
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(df.index, rsi, color='purple')
    ax.axhline(y=70, color='red', linestyle='--')
    ax.axhline(y=30, color='green', linestyle='--')
    ax.set_title('Relative Strength Index (RSI)')
    ax.set_xlabel('Date')
    ax.set_ylabel('RSI')
    ax.set_ylim(0, 100)
    ax.grid(True)
    
    return fig

def create_macd_chart(df):
    """Create MACD chart with Matplotlib"""
    if df.empty:
        return None
    
    macd_line, signal_line, histogram = calculate_macd(df['close'])
    
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(df.index, macd_line, color='blue', label='MACD Line')
    ax.plot(df.index, signal_line, color='red', label='Signal Line')
    
    # Plot histogram as bar chart
    for i, value in enumerate(histogram):
        color = 'green' if value >= 0 else 'red'
        ax.bar(df.index[i], value, color=color, width=1, alpha=0.5)
    
    ax.set_title('MACD Indicator')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.legend()
    ax.grid(True)
    
    return fig

def create_portfolio_pie_chart():
    """Create portfolio distribution pie chart"""
    summary = portfolio_analyzer.get_portfolio_summary()
    positions = pd.DataFrame(summary['positions'])
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(positions['value'], labels=positions['symbol'], autopct='%1.1f%%', 
           shadow=True, startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    ax.set_title('Portfolio Distribution')
    
    return fig

@app.route('/')
def index():
    """Render the main dashboard page"""
    symbol = request.args.get('symbol', DEFAULT_SYMBOL)
    
    # Get stock data
    df = prepare_stock_data(symbol)
    
    # Create charts
    charts = {}
    if not df.empty:
        charts['price_chart'] = fig_to_base64(create_price_chart(df))
        charts['volume_chart'] = fig_to_base64(create_volume_chart(df))
        charts['rsi_chart'] = fig_to_base64(create_rsi_chart(df))
        charts['macd_chart'] = fig_to_base64(create_macd_chart(df))
    
    # Get portfolio data
    portfolio_summary = portfolio_analyzer.get_portfolio_summary()
    portfolio_chart = fig_to_base64(create_portfolio_pie_chart())
    
    # Prepare template data
    template_data = {
        'symbol': symbol,
        'charts': charts,
        'portfolio': {
            'value': f"${portfolio_summary['metrics']['total_value']:,.2f}",
            'return': f"{portfolio_summary['metrics']['return']*100:.2f}%",
            'positions': portfolio_summary['positions'],
            'chart': portfolio_chart
        }
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
            return jsonify({'success': True, 'redirect': '/'})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True)