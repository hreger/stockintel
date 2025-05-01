import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portfolio.portfolio_analyzer import PortfolioAnalyzer

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Initialize portfolio analyzer
portfolio_analyzer = PortfolioAnalyzer()

# Sample data - replace with real data in production
portfolio_analyzer.add_position('AAPL', 100, 150.0)
portfolio_analyzer.add_position('MSFT', 50, 300.0)
portfolio_analyzer.add_position('GOOGL', 30, 2800.0)

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("StockIntel Dashboard", className="text-center mb-4"),
        ])
    ]),
    
    dbc.Row([
        # Portfolio Summary Card
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Portfolio Summary"),
                dbc.CardBody([
                    html.H4(id="portfolio-value"),
                    html.P("Total Portfolio Value"),
                    html.H4(id="portfolio-return"),
                    html.P("Total Return"),
                ])
            ], className="mb-4")
        ], width=4),
        
        # Position Distribution Chart
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Position Distribution"),
                dbc.CardBody([
                    dcc.Graph(id="position-distribution")
                ])
            ])
        ], width=8)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Positions"),
                dbc.CardBody([
                    html.Div(id="positions-table")
                ])
            ])
        ])
    ], className="mt-4")
], fluid=True)

# Callbacks
@app.callback(
    [Output("portfolio-value", "children"),
     Output("portfolio-return", "children"),
     Output("position-distribution", "figure"),
     Output("positions-table", "children")],
    Input("interval-component", "n_intervals")
)
def update_dashboard(n):
    # Get portfolio summary
    summary = portfolio_analyzer.get_portfolio_summary()
    
    # Portfolio value
    portfolio_value = f"${summary['metrics']['total_value']:,.2f}"
    
    # Portfolio return
    portfolio_return = f"{summary['metrics']['return']*100:.2f}%"
    
    # Position distribution pie chart
    positions = pd.DataFrame(summary['positions'])
    fig = go.Figure(data=[go.Pie(
        labels=positions['symbol'],
        values=positions['value'],
        hole=.3
    )])
    
    # Positions table
    table = dbc.Table.from_dataframe(
        positions[['symbol', 'quantity', 'price', 'value', 'weight', 'return']],
        striped=True,
        bordered=True,
        hover=True
    )
    
    return portfolio_value, portfolio_return, fig, table

# Add interval component for real-time updates
app.layout.children.append(
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Update every minute
        n_intervals=0
    )
)

def create_layout():
    return html.Div([
        # Header
        html.Div([
            html.H1("StockIntel Dashboard"),
            html.Div([
                dcc.Input(
                    id='stock-input',
                    type='text',
                    placeholder='Enter Stock Symbol (e.g., AAPL)',
                    className='stock-input'
                ),
                html.Button('Analyze', id='analyze-button', n_clicks=0)
            ], className='stock-search')
        ], className='header'),

        # Time Period Selector
        html.Div([
            dcc.RadioItems(
                id='timeframe-selector',
                options=[
                    {'label': 'Day', 'value': '1D'},
                    {'label': 'Week', 'value': '1W'},
                    {'label': 'Month', 'value': '1M'},
                    {'label': '1 Year', 'value': '1Y'},
                    {'label': '5 Years', 'value': '5Y'}
                ],
                value='1D',
                className='timeframe-selector'
            )
        ]),

        # Main Content Grid
        html.Div([
            # Stock Analysis Section
            html.Div([
                html.H2("Stock Analysis"),
                
                # Market Data
                html.Div([
                    html.H3("Market Data"),
                    dcc.Graph(id='price-chart'),
                    html.Div(id='ohlcv-data', className='metrics-grid'),
                    dcc.Graph(id='volume-chart'),
                    dcc.Graph(id='technical-indicators')
                ], className='analysis-section'),

                # Company Data
                html.Div([
                    html.H3("Company Information"),
                    html.Div(id='company-info', className='company-grid'),
                    html.Div(id='financial-metrics', className='metrics-grid'),
                    html.Div(id='company-news', className='news-feed')
                ], className='analysis-section'),

                # Sentiment Analysis
                html.Div([
                    html.H3("Market Sentiment"),
                    dcc.Graph(id='sentiment-gauge'),
                    html.Div(id='sentiment-breakdown', className='sentiment-grid'),
                    html.Div(id='social-sentiment', className='social-feed')
                ], className='analysis-section')
            ], className='stock-analysis'),

            # Top Performers Section
            html.Div([
                html.H2("Top Performing Stocks"),
                html.Div([
                    dcc.Graph(id='top-performers-chart'),
                    html.Div(id='top-performers-metrics', className='performers-grid'),
                    html.Div(id='performers-comparison', className='comparison-table')
                ], className='top-performers')
            ], className='performers-section')
        ], className='main-content')
    ])

if __name__ == '__main__':
    app.run(debug=True)