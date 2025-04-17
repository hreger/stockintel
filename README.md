# StockIntel: AI-Powered Market Analysis

## 📌 Features
- Real-time trend predictions using LSTM
- Company health reports (Revenue, Debt, Leadership)
- Portfolio risk scoring (VaR, Sharpe Ratio)
- Explainable AI: "Why this stock?" section
- Portfolio Analysis Dashboard
- Risk Management Metrics
- Efficient Frontier Optimization
- Stress Testing Scenarios
- Personalized User Onboarding
- SHAP-based Model Explanations

## 🚀 Quick Start
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set API keys in `.env`:
```bash
ALPHA_VANTAGE_KEY=your_key
POLYGON_KEY=your_key
```

3. Run stream processor:
```bash
python data_ingestion/kafka_producer.py
```

4. Start the dashboard:
```bash
python dashboard/app.py
```

## 📊 Data Flow
```
graph LR
A[Market APIs] --> B{Kafka}
B --> C[LSTM Model]
C --> D[Risk Calculator]
D --> E[Portfolio Analyzer]
E --> F[Dashboard]
F --> G[Explainable AI]
G --> H[User Onboarding]
```

## 🤖 Models Used
| Purpose                | Algorithm       | Accuracy  |
|------------------------|-----------------|-----------|
| Price Prediction       | LSTM            | 89.2% MAE |
| Risk Assessment        | Monte Carlo     | 92% CI    |
| Portfolio Optimization | Markowitz       | N/A       |
| Model Explanation      | SHAP            | N/A       |

## 🎯 Implementation Phases

### Phase 1: Core Infrastructure (6 Weeks)
- Real-time data pipeline with Kafka
- Basic ARIMA predictions
- Company profile scraper
- Database setup with TimescaleDB

### Phase 2: Portfolio Analysis (4 Weeks)
- Portfolio performance tracking
- Risk metrics visualization
- Efficient frontier optimization
- Stress testing scenarios
- Sector exposure analysis
- Interactive dashboard

### Phase 3: User Experience (2 Weeks)
- Explainable AI with SHAP values
- User onboarding flow
- Personalized recommendations
- Risk tolerance assessment
- Notification preferences
- User configuration management

## 🔍 Explainable AI Features
- SHAP-based feature importance
- Human-readable explanations
- Technical indicator analysis
- Risk factor breakdown
- Model confidence metrics

## 👤 User Onboarding
- Risk tolerance assessment
- Investment horizon selection
- Sector preferences
- Watchlist management
- Notification settings
- Personalized portfolio recommendations

## 📜 License
MIT License - See [LICENSE.md](LICENSE.md)

## 📫 Contact

LinkedIn Link - [P Sanjeev Pradeep](https://www.linkedin.com/in/p-sanjeev-pradeep)

Project Link: [https://github.com/hreger/stockintel](https://github.com/hreger/stockintel)

---

<p align="center">Made with ❤️ by [P Sanjeev Pradeep]</p>
