import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from portfolio.portfolio_analyzer import PortfolioAnalyzer
from dashboard.portfolio_dashboard import PortfolioDashboard

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# Initialize components
analyzer = PortfolioAnalyzer()
dashboard = PortfolioDashboard()

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("StockIntel Portfolio Dashboard", className="text-center my-4"))
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H3("Portfolio Input"),
            dbc.Input(id="portfolio-input", placeholder="Enter stock symbols (comma-separated)"),
            dbc.Input(id="weights-input", placeholder="Enter weights (comma-separated)"),
            dbc.Button("Analyze", id="analyze-button", color="primary", className="mt-2")
        ], width=4),
        
        dbc.Col([
            dcc.Graph(id="performance-chart")
        ], width=8)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="risk-metrics-chart")
        ], width=6),
        
        dbc.Col([
            dcc.Graph(id="sector-exposure-chart")
        ], width=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="efficient-frontier-chart")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="stress-test-chart")
        ], width=12)
    ])
], fluid=True)

@app.callback(
    [Output("performance-chart", "figure"),
     Output("risk-metrics-chart", "figure"),
     Output("sector-exposure-chart", "figure"),
     Output("efficient-frontier-chart", "figure"),
     Output("stress-test-chart", "figure")],
    [Input("analyze-button", "n_clicks")],
    [State("portfolio-input", "value"),
     State("weights-input", "value")]
)
def update_dashboard(n_clicks, symbols, weights):
    if n_clicks is None:
        return {}, {}, {}, {}, {}
    
    # Parse inputs
    symbols = [s.strip() for s in symbols.split(",")]
    weights = [float(w.strip()) for w in weights.split(",")]
    weights = {s: w for s, w in zip(symbols, weights)}
    
    # TODO: Fetch historical data from database
    # For now, using sample data
    dates = pd.date_range(start="2020-01-01", end="2023-01-01", freq="D")
    data = {s: np.random.randn(len(dates)).cumsum() for s in symbols}
    historical_prices = pd.DataFrame(data, index=dates)
    
    # Calculate returns
    returns = analyzer.calculate_returns(historical_prices)
    
    # Create charts
    performance_fig = dashboard.create_portfolio_performance_chart(historical_prices, weights)
    risk_metrics_fig = dashboard.create_risk_metrics_chart(returns, weights)
    
    # Sample sector data
    sector_data = {s: f"Sector {i%3}" for i, s in enumerate(symbols)}
    sector_exposure_fig = dashboard.create_sector_exposure_chart(weights, sector_data)
    
    efficient_frontier_fig = dashboard.create_efficient_frontier(returns)
    
    # Sample stress test scenarios
    scenarios = [
        {"AAPL": -0.2, "MSFT": -0.1},  # Tech sector downturn
        {"AAPL": 0.2, "MSFT": 0.1},    # Tech sector boom
        {s: -0.15 for s in symbols}     # Market crash
    ]
    stress_test_fig = dashboard.create_stress_test_chart(returns, weights, scenarios)
    
    return (performance_fig, risk_metrics_fig, sector_exposure_fig, 
            efficient_frontier_fig, stress_test_fig)

if __name__ == "__main__":
    app.run_server(debug=True) 