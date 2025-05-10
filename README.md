# 🚀 StockIntel - Your AI-Powered Stock Market Intelligence Platform

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status">
</div>

> **StockIntel** is your all-in-one AI trading assistant, combining real-time market data, advanced analytics, and machine learning to empower smarter investment decisions. Whether you're a seasoned trader or just starting out, StockIntel delivers actionable insights and a seamless user experience.

---

## 🌟 Features

- **Real-Time Market Data**: Stream and analyze live stock data from Alpha Vantage.
- **Technical & Fundamental Analysis**: RSI, MACD, Bollinger Bands, financial ratios, and more.
- **AI-Powered Predictions**: Machine learning models for price forecasting and pattern detection.
- **Sentiment Analysis**: Gauge market mood from news and social media.
- **Backtesting & Strategy Evaluation**: Test trading strategies on historical data.
- **Portfolio Management**: Optimize and track your investments.
- **Market Scanner**: Identify real-time trading opportunities.
- **Interactive Dashboard**: Visualize data and analytics in a responsive web interface.
- **Risk Management**: Advanced metrics and alerts to manage exposure.

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **FastAPI** (API backend)
- **Dash** (Web dashboard)
- **Kafka** (Real-time data streaming)
- **PostgreSQL** (Data storage)
- **TensorFlow** (Machine learning)
- **Alpha Vantage** (Market data provider)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Kafka 2.8+
- Alpha Vantage API key

### Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/hreger/stockintel.git
    cd stockintel
    ```

2. **Set up your environment**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On Unix or MacOS
    source venv/bin/activate

    pip install -r requirements.txt
    ```

3. **Configure environment variables**
    Create a `.env` file in the project root:
    ```env
    ALPHA_VANTAGE_KEY=your_actual_api_key_here
    KAFKA_BOOTSTRAP_SERVERS=localhost:9092
    DATABASE_URL=postgresql://postgres:your_password@localhost:5432/stockintel
    DEBUG=True
    LOG_LEVEL=INFO
    ```

4. **Start services**
    ```bash
    # Start PostgreSQL (if not running)
    net start postgresql

    # Start Kafka (in separate terminals)
    .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
    .\bin\windows\kafka-server-start.bat .\config\server.properties

    # Start application components (in separate terminals)
    python data_ingestion/kafka_producer.py
    python data_ingestion/kafka_consumer.py
    python prediction_service/prediction_service.py
    python dashboard/app.py
    ```

---

## 📁 Project Structure

```
stockintel/
├── data_ingestion/          # Data collection and processing
│   ├── kafka_producer.py    # Kafka producer for stock data
│   ├── kafka_consumer.py    # Kafka consumer for data processing
│   ├── init_db.py          # Database initialization
│   └── check_data.py       # Data verification
├── prediction_service/      # Machine learning predictions
│   ├── prediction_service.py # FastAPI service
│   ├── models/             # ML models
│   └── utils/              # Helper functions
├── dashboard/              # Web interface
│   ├── app.py             # Dash application
│   ├── components/        # UI components
│   └── layouts/           # Page layouts
├── portfolio/             # Portfolio management
│   └── portfolio_analyzer.py # Portfolio analysis
├── backtesting/           # Strategy testing
│   └── strategy_tester.py # Backtesting engine
├── scanner/               # Market scanning
│   └── market_scanner.py  # Opportunity scanner
├── requirements.txt       # Project dependencies
└── .env                  # Environment variables
```

## 🤝 Contributing

We love contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

Got questions? We're here to help!
- 🐛 Open an issue in the GitHub repository
- 💭 Join our [Discord community](https://discord.gg/your-discord-link)
- 📧 Email us at support@stockintel.com

## 🙏 Acknowledgments

A big thank you to:
- [Alpha Vantage](https://www.alphavantage.co/) for providing market data
- [Apache Kafka](https://kafka.apache.org/) for real-time data streaming
- [PostgreSQL](https://www.postgresql.org/) for reliable data storage
- The amazing open-source community for their contributions

---

<div align="center">
  <p>Made with ❤️ by the StockIntel Team</p>
  <p>© 2024 StockIntel. All rights reserved.</p>
</div>
