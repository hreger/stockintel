from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from datetime import datetime, timedelta

def register_callbacks(app):
    @app.callback(
        [Output('price-chart', 'figure'),
         Output('ohlcv-data', 'children'),
         Output('company-info', 'children'),
         Output('sentiment-gauge', 'figure'),
         Output('top-performers-chart', 'figure')],
        [Input('analyze-button', 'n_clicks'),
         Input('timeframe-selector', 'value')],
        [State('stock-input', 'value')]
    )
    def update_analysis(n_clicks, timeframe, symbol):
        if not symbol:
            return [{}, [], [], {}, {}]
        
        # Get market data
        market_data = get_market_data(symbol, timeframe)
        
        # Get company information
        company_info = get_company_info(symbol)
        
        # Get sentiment data
        sentiment_data = get_sentiment_data(symbol)
        
        # Get top performers
        top_performers = get_top_performers(timeframe)
        
        # Create visualizations
        price_chart = create_price_chart(market_data)
        ohlcv_display = create_ohlcv_display(market_data)
        company_display = create_company_display(company_info)
        sentiment_gauge = create_sentiment_gauge(sentiment_data)
        performers_chart = create_performers_chart(top_performers)
        
        return [price_chart, ohlcv_display, company_display, 
                sentiment_gauge, performers_chart]