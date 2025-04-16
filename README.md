# StockIntel: AI-Powered Market Analysis

## 📌 Features
- Real-time trend predictions using LSTM
- Company health reports (Revenue, Debt, Leadership)
- Portfolio risk scoring (VaR, Sharpe Ratio)
- Explainable AI: "Why this stock?" section

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

## 📊 Data Flow
```
graph LR
A[Market APIs] --> B{Kafka}
B --> C[LSTM Model]
C --> D[Risk Calculator]
D --> E[React Dashboard]
```

## 🤖 Models Used
| Purpose                | Algorithm       | Accuracy  |
|------------------------|-----------------|-----------|
| Price Prediction       | LSTM            | 89.2% MAE |
| Risk Assessment        | Monte Carlo     | 92% CI    |

## 📜 License
MIT License - See [LICENSE.md](LICENSE.md)

## 📫 Contact

LinkedIn Link - [P Sanjeev Pradeep](https://www.linkedin.com/in/p-sanjeev-pradeep)

Project Link: [https://github.com/hreger/stockintel](https://github.com/hreger/stockintel)

---

<p align="center">Made with ❤️ by [P Sanjeev Pradeep]</p>
