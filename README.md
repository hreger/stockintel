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
```

## 🤖 Models Used
| Purpose                | Algorithm       | Accuracy  |
|------------------------|-----------------|-----------|
| Price Prediction       | LSTM            | 89.2% MAE |
| Risk Assessment        | Monte Carlo     | 92% CI    |
| Portfolio Optimization | Markowitz       | N/A       |

## 🎯 Phase 2 Features
### Portfolio Analysis
- Real-time portfolio performance tracking
- Sector exposure analysis
- Risk metrics visualization (VaR, Sharpe Ratio)
- Efficient frontier optimization
- Stress testing scenarios

### Risk Management
- Value at Risk (VaR) calculations
- Portfolio stress testing
- Sector diversification analysis
- Risk-adjusted return metrics

## 📜 License
MIT License - See [LICENSE.md](LICENSE.md)

## 📫 Contact

LinkedIn Link - [P Sanjeev Pradeep](https://www.linkedin.com/in/p-sanjeev-pradeep)

Project Link: [https://github.com/hreger/stockintel](https://github.com/hreger/stockintel)

---

<p align="center">Made with ❤️ by [P Sanjeev Pradeep]</p>
