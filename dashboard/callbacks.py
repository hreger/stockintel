from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from datetime import datetime, timedelta

def register_callbacks(app):
    @app.callback(
        [Output('price-chart', 'figure'),
         Output('volume-chart', 'figure'),
         Output('rsi-chart', 'figure'),
         Output('macd-chart', 'figure')],
        [Input('analyze-button', 'n_clicks'),
         Input('timeframe-selector', 'value')],
        [State('stock-input', 'value')]
    )
    def update_analysis(n_clicks, timeframe, symbol):
        if not symbol:
            return [{}, {}, {}, {}]
        
        # Get market data
        market_data = get_market_data(symbol, timeframe)
        print(f"Market data for {symbol}: {market_data}")  # Debugging line
        
        # Create visualizations for each chart
        price_chart = create_price_chart(market_data)
        volume_chart = create_volume_chart(market_data)
        rsi_chart = create_rsi_chart(market_data)
        macd_chart = create_macd_chart(market_data)
        
        return [price_chart, volume_chart, rsi_chart, macd_chart]