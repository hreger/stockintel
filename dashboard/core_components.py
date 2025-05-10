import dash
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class CoreDashboardComponents:
    def create_stock_chart(self, data, indicators=None):
        """Create main stock chart with optional indicators"""
        # Create figure with secondary y-axis for volume
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3]
        )
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data['date'],
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name="OHLC"
            ),
            row=1, col=1
        )
        
        # Add volume bar chart
        fig.add_trace(
            go.Bar(
                x=data['date'],
                y=data['volume'],
                name="Volume"
            ),
            row=2, col=1
        )
        
        # Add indicators if provided
        if indicators:
            if 'sma_50' in indicators:
                fig.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=indicators['sma_50'],
                        line=dict(color='blue', width=1),
                        name="50-day SMA"
                    ),
                    row=1, col=1
                )
            
            if 'sma_200' in indicators:
                fig.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=indicators['sma_200'],
                        line=dict(color='red', width=1),
                        name="200-day SMA"
                    ),
                    row=1, col=1
                )
        
        # Update layout
        fig.update_layout(
            title="Stock Price Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            height=600
        )
        
        return fig