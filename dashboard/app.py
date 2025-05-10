import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd

from data_ingestion.api_client import StockDataClient
from portfolio.portfolio_analyzer import PortfolioAnalyzer
from dashboard.components.technical_indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# Initialize components with dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY],suppress_callback_exceptions=True)
stock_client = StockDataClient()
portfolio_analyzer = PortfolioAnalyzer()

# Initialize sample portfolio data
portfolio_analyzer.add_position('AAPL', 100, 150.0)
portfolio_analyzer.add_position('MSFT', 50, 300.0)
portfolio_analyzer.add_position('GOOGL', 30, 2800.0)

# Set default stock symbol
DEFAULT_SYMBOL = 'AAPL'

# Create the layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])

# Define the main layout
main_layout = dbc.Container([
    # Login Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Login"),
                dbc.CardBody([
                    dbc.Input(id="username-input", placeholder="Username", type="text", className="mb-2"),
                    dbc.Input(id="password-input", placeholder="Password", type="password", className="mb-2"),
                    dbc.Button("Login", id="login-button", color="primary", className="me-2")
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    # Header with search
    dbc.Row([
        dbc.Col([
            html.H1("StockIntel Dashboard", className="dashboard-title"),
            dbc.Input(
                id="stock-search",
                type="text",
                value=DEFAULT_SYMBOL,  # Add this line
                placeholder="Enter stock symbol (e.g., AAPL)",
                className="stock-search"
            ),
            dbc.Button("Search", id="search-button", color="primary", className="ms-2")
        ], width=12)
    ], className="mb-4"),

    # Market Overview and Portfolio Summary
    dbc.Row([
        # Portfolio Summary Card
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Portfolio Summary"),
                dbc.CardBody([
                    html.H4(id="portfolio-value"),
                    html.P("Total Portfolio Value"),
                    html.H4(id="portfolio-return"),
                    html.P("Total Return")
                ])
            ])
        ], width=4),
        
        # Position Distribution
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Position Distribution"),
                dbc.CardBody([
                    dcc.Graph(id="position-distribution")
                ])
            ])
        ], width=8)
    ], className="mb-4"),

    # Technical Analysis Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Technical Analysis"),
                    dbc.ButtonGroup([
                        dbc.Button("1D", id="1d-btn", size="sm", n_clicks=0, className="timeframe-btn"),
                        dbc.Button("1W", id="1w-btn", size="sm", n_clicks=0, className="timeframe-btn"),
                        dbc.Button("1M", id="1m-btn", size="sm", n_clicks=0, className="timeframe-btn"),
                        dbc.Button("1Y", id="1y-btn", size="sm", n_clicks=0, className="timeframe-btn")
                    ])
                ]),
                dbc.CardBody([
                    # Add store component for timeframe
                    dcc.Store(id='selected-timeframe', data='1D'),
                    dcc.Graph(id="price-chart"),
                    dcc.Graph(id="volume-chart"),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id="rsi-chart"), width=6),
                        dbc.Col(dcc.Graph(id="macd-chart"), width=6)
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),

    # Positions Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Portfolio Positions"),
                dbc.CardBody([
                    html.Div(id="positions-table")
                ])
            ])
        ], width=12)
    ]),

    # Stock Trend Predictions Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Stock Trend Predictions"),
                dbc.CardBody([
                    dcc.Graph(id="prediction-chart"),
                    html.Div([
                        html.Div([
                            html.Span("3-Month Growth: ", className="prediction-label"),
                            html.Span("+15%", id="three-month-growth", className="prediction-value positive")
                        ], className="prediction-metric"),
                        html.Div([
                            html.Span("6-Month Growth: ", className="prediction-label"),
                            html.Span("-3%", id="six-month-growth", className="prediction-value negative")
                        ], className="prediction-metric"),
                        html.Div([
                            html.Span("1-Year Growth: ", className="prediction-label"),
                            html.Span("+7%", id="one-year-growth", className="prediction-value positive")
                        ], className="prediction-metric")
                    ], className="prediction-metrics-container")
                ])
            ])
        ], width=12)
    ], className="mb-4"),

    # Company Insights Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Company Insights"),
                dbc.CardBody([
                    html.Div([
                        html.H5("TechCorp", className="company-name"),
                        html.P("Innovative solutions driving growth.", className="company-description"),
                        dcc.Graph(id="company-metrics")
                    ]),
                    html.Div([
                        html.H5("GreenEnergy", className="company-name mt-4"),
                        html.P("Sustainable energy with a promising future.", className="company-description"),
                        dcc.Graph(id="company-metrics-2")
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),

    # Actionable Investment Advice Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Actionable Investment Advice"),
                dbc.CardBody([
                    html.Div([
                        html.P("Diversify investments across sectors.", className="advice-item"),
                        html.P("Consider long-term growth potential over short-term gains.", className="advice-item"),
                        html.P("Monitor market trends and adjust portfolio accordingly.", className="advice-item")
                    ], className="advice-container")
                ])
            ])
        ], width=12)
    ]),  # Added missing comma here

    # Interval component for real-time updates
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Update every minute
        n_intervals=0
    )
], fluid=True)


# Add CSS for responsiveness
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>StockIntel Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            .dashboard-title {
                color: #2c3e50;
                margin-bottom: 1rem;
            }
            .stock-search {
                max-width: 300px;
                display: inline-block;
            }
            .card {
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
            }
            .card-header {
                background-color: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
            }
            @media (max-width: 768px) {
                .container-fluid {
                    padding: 10px;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Add CSS for styling (single definition)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>StockIntel Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            .dashboard-title {
                color: #ffffff;
                margin-bottom: 1rem;
            }
            .stock-search {
                max-width: 300px;
                display: inline-block;
            }
            .card {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
            }
            .card-header {
                background-color: #303030;
                border-bottom: 1px solid #3a3a3a;
            }
            .list-group-item {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                color: #ffffff;
            }
            .list-group-item:hover {
                background-color: #303030;
            }
            .nav-link {
                color: #ffffff;
            }
            .nav-link:hover {
                color: #007bff;
            }
            .timeframe-btn {
                margin: 0 2px;
            }
            .timeframe-btn.active {
                background-color: #0056b3;
                border-color: #0056b3;
            }
            .prediction-metrics-container {
                display: flex;
                justify-content: space-around;
                margin-top: 20px;
            }
            .prediction-metric {
                text-align: center;
            }
            .prediction-label {
                font-size: 1.1em;
                color: #aaa;
            }
            .prediction-value {
                font-size: 1.2em;
                font-weight: bold;
                margin-left: 5px;
            }
            .positive {
                color: #00ff00;
            }
            .negative {
                color: #ff0000;
            }
            .company-name {
                color: #fff;
                margin-bottom: 5px;
            }
            .company-description {
                color: #aaa;
                margin-bottom: 15px;
            }
            .advice-container {
                padding: 10px;
            }
            .advice-item {
                color: #ddd;
                margin-bottom: 10px;
                padding-left: 20px;
                position: relative;
            }
            .advice-item:before {
                content: "•";
                position: absolute;
                left: 0;
                color: #007bff;
            }
            @media (max-width: 768px) {
                .container-fluid {
                    padding: 10px;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

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
    
    # Update layout for better visualization
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Positions table
    table = dbc.Table.from_dataframe(
        positions[['symbol', 'quantity', 'price', 'value', 'weight', 'return']],
        striped=True,
        bordered=True,
        hover=True
    )
    
    return portfolio_value, portfolio_return, fig, table

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app.server)
login_manager.login_view = '/login'

# User class for authentication
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    return User(username)

# Add login callback
@app.callback(
    Output("url", "pathname"),
    [Input("login-button", "n_clicks")],
    [State("username-input", "value"),
     State("password-input", "value")]
)
def login_callback(n_clicks, username, password):
    if n_clicks is None:
        return dash.no_update
    
    # Add your authentication logic here
    if username == "admin" and password == "password":  # Replace with proper authentication
        user = User(username)
        login_user(user)
        return "/"
    return "/login"

# Define a simple login layout
login_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Login"),
                dbc.CardBody([
                    dbc.Input(id="username-input", placeholder="Username", type="text", className="mb-2"),
                    dbc.Input(id="password-input", placeholder="Password", type="password", className="mb-2"),
                    dbc.Button("Login", id="login-button", color="primary", className="me-2")
                ])
            ])
        ], width=4)
    ], className="justify-content-center align-items-center", style={"height": "100vh"})
], fluid=True)

# Protect the main layout
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/login' or not current_user.is_authenticated:
        return login_layout
    return main_layout

if __name__ == '__main__':
    app.run(debug=True)

