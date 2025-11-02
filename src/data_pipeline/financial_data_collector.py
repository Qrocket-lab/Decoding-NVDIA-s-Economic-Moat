import pandas as pd
import requests
import json
import numpy as np
from datetime import datetime
import yfinance as yf

# --- Configuration ---
API_KEY = 'Your Alpha Vantage API key'
COMPANY_TICKER = 'NVDA'
OUTPUT_CSV_FILE = 'nvidia_financial_data.csv'

# Alpha Vantage API endpoints
AV_INCOME_STATEMENT_URL = 'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={}&apikey={}'
AV_BALANCE_SHEET_URL = 'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={}&apikey={}'
AV_CASH_FLOW_URL = 'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={}&apikey={}'

# --- 1. Define Data Fetching Functions ---

def fetch_alpha_vantage_data(url, key, data_key):
    """Fetches data from Alpha Vantage and returns it as a DataFrame."""
    try:
        response = requests.get(url.format(COMPANY_TICKER, key))
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data or data_key not in data or not data[data_key]:
            print(f"Warning: No data found for {data_key} from Alpha Vantage.")
            return pd.DataFrame()

        df = pd.DataFrame(data[data_key])

        for col in df.columns:
            if col != 'fiscalDateEnding':
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df.rename(columns={'fiscalDateEnding': 'ReportDate'}, inplace=True)
        df['ReportDate'] = pd.to_datetime(df['ReportDate'])
        df.set_index('ReportDate', inplace=True)
        df['PeriodType'] = 'Quarterly'
        df = df[~df.index.duplicated(keep='first')]

        return df

    except requests.exceptions.RequestException as e:
        print(f"Request failed for Alpha Vantage: {e}")
        return pd.DataFrame()

def fetch_yfinance_data():
    """Fetches annual data from yfinance as a fallback."""
    print("Falling back to yfinance for annual data.")
    nvidia = yf.Ticker(COMPANY_TICKER)

    annual_financials = nvidia.financials.T
    annual_balance_sheet = nvidia.balance_sheet.T
    annual_cashflow = nvidia.cashflow.T

    dataframes = [annual_financials, annual_balance_sheet, annual_cashflow]

    # Process and merge yfinance data
    df_combined = pd.DataFrame()
    for df in dataframes:
        if not df.empty:
            df.index.name = 'ReportDate'
            df = df.reset_index()
            df['ReportDate'] = pd.to_datetime(df['ReportDate'])
            df.set_index('ReportDate', inplace=True)
            df['PeriodType'] = 'Annual'

            if df_combined.empty:
                df_combined = df
            else:
                df_combined = df_combined.merge(df, on='ReportDate', how='outer', suffixes=('', '_y'))
                df_combined = df_combined.loc[:, ~df_combined.columns.duplicated()]

    # Clean up column names for consistency
    if not df_combined.empty:
        df_combined.rename(columns={
            'Total Revenue': 'totalRevenue',
            'Gross Profit': 'grossProfit',
            'Operating Income': 'operatingIncome',
            'Net Income': 'netIncome',
            'Total Assets': 'totalAssets',
            'Total Liabilities Net Minority Interest': 'totalLiabilities',
            'Stockholders Equity': 'totalShareholderEquity',
            'longTermDebt': 'totalDebt',
            'Operating Cash Flow': 'operatingCashflow',
            'Capital Expenditure': 'capitalExpenditures',
            'Free Cash Flow': 'freeCashFlow'
        }, inplace=True)

    return df_combined

# --- 2. Main Logic: Try Alpha Vantage, then fallback to yfinance ---

print(f"Attempting to fetch quarterly data for {COMPANY_TICKER} from Alpha Vantage...")
income_statement = fetch_alpha_vantage_data(AV_INCOME_STATEMENT_URL, API_KEY, 'quarterlyReports')
balance_sheet = fetch_alpha_vantage_data(AV_BALANCE_SHEET_URL, API_KEY, 'quarterlyReports')
cash_flow = fetch_alpha_vantage_data(AV_CASH_FLOW_URL, API_KEY, 'quarterlyReports')

if not income_statement.empty and not balance_sheet.empty and not cash_flow.empty:
    print("Alpha Vantage data fetched successfully.")
    df_combined = income_statement.merge(balance_sheet, on='ReportDate', how='outer').merge(
        cash_flow, on='ReportDate', how='outer', suffixes=('_bs', '_cf'))
    df_combined.rename(columns={'PeriodType_cf': 'PeriodType'}, inplace=True)
    df_combined = df_combined.loc[:, ~df_combined.columns.str.endswith(('_bs', '_cf'))]
    # Keep only the last 100 entries for consistency
    df_combined = df_combined.sort_index().tail(100)
    data_source = "Alpha Vantage"
else:
    print("Alpha Vantage data is incomplete. Falling back to yfinance.")
    df_combined = fetch_yfinance_data()
    data_source = "yfinance"

if df_combined.empty:
    print("No data could be fetched from any source. Exiting.")
    exit()

# --- 3. Prepare for Power BI ---

df_combined = df_combined.reset_index()
df_combined.rename(columns={'ReportDate': 'Report Date'}, inplace=True)
df_combined['Report Date'] = pd.to_datetime(df_combined['Report Date']).dt.date

# --- 4. Save to CSV ---

df_combined.to_csv(OUTPUT_CSV_FILE, index=False)
print(f"\nSuccessfully fetched data from {data_source} and saved to {OUTPUT_CSV_FILE}")
print("The CSV is now ready for your Power BI dashboard.")

print("\nSample of Processed Data (First 5 rows):")
print(df_combined.head())

# If you have free alpha vantage account, the stock data will not be appear (due to the subscription and limitiation)
# Hence i will provide stock data using yfinance ()