import pandas as pd
import yfinance as yf
import datetime

# --- Configuration ---
COMPANY_TICKER = 'NVDA'
OUTPUT_CSV_FILE = 'nvda_stock_data.csv'

def fetch_stock_data(symbol):
    """Fetches historical daily adjusted stock data using yfinance."""
    try:
        print(f"Fetching historical stock data for {symbol} using yfinance...")

        start_date = datetime.date(1980, 1, 1)
        end_date = datetime.date.today()

        # Fetch data from Yahoo Finance via yfinance
        df = yf.download(symbol, start=start_date, end=end_date)

        if df.empty:
            print(f"Warning: No stock data found for {symbol}.")
            return pd.DataFrame()

        # --- DEBUG: Print columns to identify the correct 'Adjusted Close' column ---
        print("\nColumns available in yfinance DataFrame:")
        print(df.columns)
        # --- END DEBUG ---

        # Keep only the adjusted close price and volume
        # Access the columns using the MultiIndex structure
        stock_df = df[[('Close', symbol), ('Volume', symbol)]].copy()

        # Flatten the MultiIndex columns
        stock_df.columns = [col[0] for col in stock_df.columns]


        stock_df.reset_index(inplace=True)

        # Rename columns to be descriptive and match your date format
        stock_df.rename(columns={
            'Date': 'Report Date',
            'Close': 'adjustedCloseStockPrice', # Changed from ('Close', symbol)
            'Volume': 'dailyTradingVolume' # Changed from ('Volume', symbol)
        }, inplace=True)

        # Ensure the date format is consistent for Power BI
        stock_df['Report Date'] = pd.to_datetime(stock_df['Report Date']).dt.date

        print(f"Successfully fetched stock data for {symbol}.")
        return stock_df

    except Exception as e:
        print(f"An error occurred while fetching stock data: {e}")
        return pd.DataFrame()

# --- Main Logic ---
stock_data = fetch_stock_data(COMPANY_TICKER)

if not stock_data.empty:
    stock_data.to_csv(OUTPUT_CSV_FILE, index=False)
    print(f"\nSuccessfully saved stock data to {OUTPUT_CSV_FILE}")
else:
    print("\nNo data to save. Exiting.")

print("\nSample of Processed Data (First 5 rows):")
if not stock_data.empty:
    display(stock_data.head())