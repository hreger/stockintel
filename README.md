# StockIntel - Stock Market Intelligence Platform

StockIntel is a comprehensive stock market intelligence and trading platform that combines real-time data analysis, machine learning predictions, and market sentiment analysis to provide actionable insights for traders and investors.

## Features

- **Real-time Data Pipeline**
  - Live stock data collection from Alpha Vantage API
  - Real-time data processing with Kafka
  - PostgreSQL database storage
  - Automated data ingestion and processing

- **Market Analysis**
  - Technical analysis with multiple indicators (RSI, MACD, Bollinger Bands)
  - Fundamental analysis of company metrics
  - Market sentiment analysis from news and social media
  - Pattern recognition using machine learning

- **Trading Tools**
  - Backtesting module for strategy testing
  - Market scanner for opportunity identification
  - Portfolio optimization
  - Risk management features

- **Prediction System**
  - Machine learning models for price prediction
  - Sentiment analysis for market mood
  - Pattern recognition for technical analysis
  - Risk assessment and probability scoring

- **User Interface**
  - Interactive web dashboard
  - Real-time market data visualization
  - Technical indicator charts
  - Portfolio tracking and performance metrics

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Kafka 2.8+
- Alpha Vantage API key

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/stockintel.git
cd stockintel
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory with the following content:
```env
# API Keys
ALPHA_VANTAGE_KEY=your_actual_api_key_here  # Get from: https://www.alphavantage.co/support/#api-key

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/stockintel

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

5. **Set up PostgreSQL**
```bash
# Create database
createdb stockintel

# Initialize database schema
python data_ingestion/init_db.py
```

6. **Set up Kafka**
- Download Kafka from https://kafka.apache.org/downloads
- Extract to a directory (e.g., `C:\kafka`)
- Start Zookeeper:
```bash
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```
- Start Kafka server:
```bash
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

## Running the Application

1. **Start the Data Pipeline**
```bash
# Terminal 1 - Kafka Producer
python data_ingestion/kafka_producer.py

# Terminal 2 - Kafka Consumer
python data_ingestion/kafka_consumer.py
```

2. **Start the Prediction Service**
```bash
# Terminal 3 - Prediction Service
python prediction_service/prediction_service.py
```

3. **Start the Web Dashboard**
```bash
# Terminal 4 - Web Dashboard
python dashboard/app.py
```

4. **Verify Setup**
```bash
python data_ingestion/check_data.py
```

## Accessing the Application

- **Web Dashboard**: http://localhost:8050
- **API Documentation**: http://localhost:8000/docs

## Project Structure

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
├── backtesting/           # Strategy testing
│   └── strategy_tester.py # Backtesting engine
├── scanner/               # Market scanning
│   └── market_scanner.py  # Opportunity scanner
├── requirements.txt       # Project dependencies
└── .env                  # Environment variables
```

Now: Phase 1: Data Ingestion — Kafka Producer
(venv) PS C:\Users\psp17\stockintel> python data_ingestion\kafka_producer.py

Produced data for AAPL: {'symbol': 'AAPL', 'price': 194.27, 'volume': 59732423, 'timestamp': '2025-04-16'}

Produced data for MSFT: {'symbol': 'MSFT', 'price': 371.61, 'volume': 21967826, 'timestamp': '2025-04-16'}

Produced data for GOOGL: {'symbol': 'GOOGL', 'price': 153.33, 'volume': 28187421, 'timestamp': '2025-04-16'}

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- Alpha Vantage for providing stock market data
- Apache Kafka for real-time data streaming
- PostgreSQL for reliable data storage
- The open-source community for various libraries and tools
