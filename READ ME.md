# NVIDIA Moat Analysis - Complete GitHub Repository Documentation

## Project Overview

**NVIDIA Moat Analysis** is a comprehensive financial analytics project that combines Power BI dashboarding with machine learning forecasting to analyze NVIDIA's competitive advantages and financial performance. The project demonstrates end-to-end data pipeline development from data extraction to interactive visualization and predictive modeling.

## Data Flow

```
Alpha Vantage API → financial_data_collector.py → data/raw/ → data_processor.py → data/processed/
     ↓
yfinance API → stock_data_collector.py → data/raw/ → data_processor.py → data/processed/
     ↓
processed data → forecasting_engine.py → data/forecasts/ → Power BI Dashboard
     ↓
two_stage_forecast.py → enhanced forecasts → data/forecasts/
```

## Project Architecture

```
NVIDIA_Moat_Analysis/
│
├── 📁 data/
│   ├── 📁 raw/                          # Raw data from APIs
│   │   └── nvidia_financial_data.csv    # Raw data from Alpha Vantage
│   │
│   ├── 📁 processed/                    # Cleaned and processed data
│   │   ├── nvidia_financial_data_DAX.csv
│   │   ├── nvda_stock_data.csv
│   │   └── calendar_table.csv
│   │
│   └── 📁 forecasts/                    # Model predictions
│       ├── kpi_forecast.csv
│       └── price_forecast.csv
│
├── 📁 src/
│   ├── 📁 data_pipeline/
│   │   ├── financial_data_collector.py
│   │   └── stock_data_collector.py
│   │
│   ├── 📁 machine_learning/
│   │   ├── forecasting_engine.py
│   └── └── two_stage_forecast.py
│
├── 📁 powerbi/
│   ├──  All_DAX_Formulas.md
│   └──  data_model_schema.png 
│
├── 📁 docs/
│   ├── project_overview.md
│   ├── api_documentation.md
│   ├── deployment_guide.md
│   └── methodology.md
│
├── requirements.txt
├── main.py                             # Main execution script
├── config.yaml                         # Configuration file
└── README.md
```

## Quick Start

### Prerequisites
```bash
pip install pandas numpy scikit-learn xgboost yfinance requests
```

### Data Collection & Processing
1. **Financial Data Extraction** (`data_collection.py`)
2. **Stock Data Collection** (`stock_data_collection.py`)
3. **Run Forecasting Models** (`forecasting_models.py`)

### Power BI Setup
1. Import generated CSV files
2. Establish relationships using Calendar table
3. Refresh data and explore interactive dashboard

## File Structure

### Core Python Scripts

#### 1. Financial Data Collection (`financial_data_collector.py`)
```python
# Key Features:
# - Fetches quarterly financial statements from Alpha Vantage
# - Merges Income Statement, Balance Sheet, and Cash Flow
# - Handles API rate limits and data validation
# - Output: nvidia_combined_financial_data.csv
```

#### 2. Stock Data Collection (`stock_data_collector.py`)
```python
# Key Features:
# - Historical daily stock data via yfinance
# - Adjusted close prices and trading volume
# - Date range: 1980 to current
# - Output: nvda_stock_data.csv
```

#### 3. Forecasting Engine (`forecasting_engine.py`)
```python
# Key Models Implemented:
# - Linear Regression (baseline)
# - Random Forest Regressor
# - XGBoost (best performance)
# - Two-stage forecasting approach
```

#### 4. Two-Stage Forecasting (`two_stage_forecast.py`)
```python
# Stage 1: KPI Forecasting (ROIC, Gross Margin, R&D %, FCF)
# Stage 2: Stock Price Prediction using forecasted KPIs
# Output: kpi_forecast.csv, price_forecast.csv
```

### Data Files
- `nvidia_financial_data_DAX.csv` - Pre-calculated financial metrics
- `nvda_stock_data.csv` - Historical stock performance
- `kpi_forecast.csv` - Forecasted financial KPIs
- `price_forecast.csv` - Predicted stock prices

## Technical Implementation

### Data Pipeline Architecture

#### 1. Data Extraction Layer
```python
# Alpha Vantage API Integration
def fetch_alpha_vantage_quarterly_data(url, key, data_key):
    # Handles quarterly financial data
    # Automatic numeric conversion and date parsing

# Yahoo Finance Integration  
def fetch_stock_data(symbol):
    # Daily adjusted close and volume
    # Robust error handling for API limits
```

#### 2. Data Processing & Feature Engineering
```python
# Key Processing Steps:
# - Date standardization across datasets
# - Percentage column cleaning (ROIC %, Gross Margin %)
# - Lagged feature creation for time series
# - Missing value handling and validation
```

#### 3. Machine Learning Pipeline
```python
# Feature Engineering:
combined_df['target_price'] = combined_df['adjustedCloseStockPrice'].shift(-1)
combined_df[f'lagged_{kpi}'] = combined_df[kpi].shift(1)

# Model Training:
models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(),
    'XGBoost': XGBRegressor()
}
```

### Forecasting Methodology

#### Two-Stage Approach:
1. **Stage 1 - KPI Forecasting**
   - Linear regression on time-indexed financial KPIs
   - Forecasts: ROIC %, Gross Margin %, R&D %, Free Cash Flow
   - Horizon: 2 quarters forward

2. **Stage 2 - Stock Price Forecasting**
   - XGBoost model using lagged KPIs and historical prices
   - Incorporates Stage 1 forecasts as features
   - Predicts next quarter stock price

## Power BI Data Model

### Schema Relationships
```
Calendar Table (Date)
    │
    ├── Financial Data (Report Date)
    │   ├── ROIC, Gross Margin, R&D %, FCF
    │   └── Calculated KPIs via DAX
    │
    ├── Stock Data (Report Date)  
    │   ├── Adjusted Close Price
    │   └── Daily Trading Volume
    │
    └── Forecast Data (Report Date)
        ├── Forecasted KPIs
        └── Predicted Stock Prices
```

### Key DAX Calculations
please see powerbi folder

## Dashboard Components

### Overview Tab
- **KPI Cards**: Total Revenue, Gross Profit, Net Income, EBITDA
- **Trend Analysis**: Revenue vs. Gross Profit comparison
- **Performance Metrics**: R&D Spending, CAPEX, Free Cash Flow
- **Waterfall Chart**: Income statement breakdown

### Moat Analysis Tab
- **ROIC Trend**: Return on Invested Capital over time
- **Gross Margin Analysis**: Profitability sustainability
- **R&D Efficiency**: Innovation investment returns
- **Competitive Advantage Indicators**

### Ratios Tab  
- **Valuation Ratios**: P/E, P/BV, EV/EBITDA
- **Profitability**: Net Margin, ROE, ROA
- **Liquidity & Solvency**: Current Ratio, Debt-to-Equity
- **Efficiency**: Asset Turnover, Inventory Days

## Model Performance

### Forecasting Accuracy
```
XGBoost Model (Best Performer):
- Mean Absolute Error: $7.14
- R-squared: 0.96

Random Forest:
- Mean Absolute Error: $15.96  
- R-squared: 0.84

Linear Regression:
- Mean Absolute Error: $12.67
- R-squared: 0.82
```

## Usage Instructions

### 1. Data Collection
```bash
python financial_data_collector.py
python stock_data_collector.py
```

### 2. Run Forecasting
```bash
python forecasting_engine.py
python two_stage_forecast.py
```

### 3. Power BI Setup
1. Open `NVIDIA_Moat_Analysis.pbix`
2. Configure data source paths
3. Refresh data connections
4. Explore interactive visualizations

## Future Enhancements

### Planned Improvements
- [ ] Real-time data streaming integration
- [ ] Additional ML models (LSTM, Prophet)
- [ ] Sentiment analysis integration
- [ ] Peer comparison analytics
- [ ] Automated reporting and alerts

### Technical Debt
- [ ] API key management system
- [ ] Error handling and logging improvement
- [ ] Unit test coverage
- [ ] Docker containerization

## Documentation Files

### Required Documentation
- `README.md` - Project overview and setup instructions
- `API_DOCUMENTATION.md` - Data source integration guide
- `DAX_FORMULAS.md` - Power BI calculation documentation
- `MODEL_DETAILS.md` - Machine learning model specifications
- `DEPLOYMENT_GUIDE.md` - Production deployment instructions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Alpha Vantage for financial data API
- Yahoo Finance for historical stock data
- Microsoft Power BI for visualization platform
- Scikit-learn and XGBoost communities

---

**Contact**: [qodrimuhamad98@gmail.com](Ask me)  
**Other Project**: [https://qrocketlab.xyz/](Portofolio)

*Last Updated: [Current Date]*