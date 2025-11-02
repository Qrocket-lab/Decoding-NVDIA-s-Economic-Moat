import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from datetime import timedelta

def two_stage_forecast():
    """
    Implements a two-stage forecasting model with two separate data tables.
    Stage 1: Predicts future KPIs from historical financial data.
    Stage 2: Predicts future stock price using historical stock data and forecasted KPIs.
    """
    try:
        # --- Data Loading ---
        print("Loading and preparing data...")

        # Load financial data with the correct filename
        financial_df = pd.read_csv('nvidia_financial_data_DAX.csv')

        # Load stock data (with Report Date)
        stock_df = pd.read_csv('nvda_stock_data.csv')
        stock_df['Report Date'] = pd.to_datetime(stock_df['Report Date'])
        stock_df.sort_values('Report Date', inplace=True)

    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure both files are in the same folder and have the correct names.")
        print(f"I was looking for 'nvda_dax.csv' and 'nvda_stock_data.csv'")
        return
    except KeyError as e:
        print(f"Error: Missing expected column {e}. Please check your CSV file headers.")
        return

    # --- Data Preparation: Handle Missing Values and Create 'Report Date' ---
    print("Checking for and removing rows with missing 'Year' or 'Quarter'...")
    financial_df.dropna(subset=['Year', 'Quarter'], inplace=True)

    # *** IMPORTANT FIX: Clean the 'Quarter' column to remove the "Qtr " string ***
    print("Cleaning 'Quarter' column...")
    financial_df['Quarter'] = financial_df['Quarter'].astype(str).str.replace('Qtr ', '').astype(int)

    # Create 'Report Date' from 'Year' and 'Quarter' columns
    print("Creating 'Report Date' from 'Year' and 'Quarter' columns...")

    # Map quarter to a month to create a valid date
    quarter_to_month = {1: '03-31', 2: '06-30', 3: '09-30', 4: '12-31'}
    financial_df['Report Date'] = financial_df['Year'].astype(str) + '-' + financial_df['Quarter'].map(quarter_to_month).astype(str)
    financial_df['Report Date'] = pd.to_datetime(financial_df['Report Date'], errors='coerce')

    # Remove rows with invalid dates (NaT) to prevent merge error
    print("Removing rows where 'Report Date' is invalid...")
    financial_df.dropna(subset=['Report Date'], inplace=True)
    financial_df.sort_values('Report Date', inplace=True)

    # --- VERIFICATION STEP ---
    if financial_df.empty:
        print("\nError: The financial data DataFrame is empty after cleaning. Please check your source file for complete rows.")
        return

    # --- Clean pre-calculated KPI columns and correctly define list ---
    print("Cleaning pre-calculated KPI columns...")

    kpis_to_forecast = ['ROIC (%)', 'Gross Margin %', 'R&D as % of Revenue', 'Free Cash Flow']

    for kpi in kpis_to_forecast:
        if kpi not in financial_df.columns:
            print(f"Warning: KPI column '{kpi}' not found. Skipping cleaning for this column.")
            continue

        financial_df[kpi] = financial_df[kpi].astype(str).str.rstrip('%').replace('', np.nan)
        financial_df[kpi] = pd.to_numeric(financial_df[kpi], errors='coerce')

    # --- Stage 1: KPI Forecasting ---
    print("\nStage 1: Forecasting financial KPIs...")

    forecast_horizon = 2
    financial_df['time_index'] = range(len(financial_df))

    kpi_forecasts = pd.DataFrame()
    kpi_forecasts['Report Date'] = [
        financial_df['Report Date'].iloc[-1] + timedelta(days=90 * (i + 1)) for i in range(forecast_horizon)
    ]

    for kpi in kpis_to_forecast:
        if kpi not in financial_df.columns:
            continue

        model = LinearRegression()
        X = financial_df[['time_index']].dropna()
        y = financial_df[kpi].dropna()

        if len(X) > 1 and len(y) > 1:
            model.fit(X, y)
            future_time_indices = np.array(range(len(financial_df), len(financial_df) + forecast_horizon)).reshape(-1, 1)
            kpi_forecasts[kpi] = model.predict(future_time_indices)
        else:
            kpi_forecasts[kpi] = np.nan

    kpi_forecasts.to_csv('kpi_forecast.csv', index=False)
    print("KPI forecast saved to 'kpi_forecast.csv'")

    # --- Stage 2: Stock Price Forecasting ---
    print("\nStage 2: Forecasting stock price...")

    # Merge financial and stock data using the newly created 'Report Date' column
    historical_combined_df = pd.merge_asof(
        financial_df,
        stock_df,
        left_on='Report Date',
        right_on='Report Date',
        direction='nearest'
    )

    # Correctly reference the stock price column and drop missing rows
    columns_to_check = ['adjustedCloseStockPrice'] + [col for col in kpis_to_forecast if col in historical_combined_df.columns]
    historical_combined_df.dropna(subset=columns_to_check, inplace=True)

    # --- VERIFICATION STEP ---
    if historical_combined_df.empty:
        print("\nError: The combined DataFrame is empty after merging. This means there's no matching historical data for the forecast.")
        print("Please check your financial and stock data files to ensure their dates overlap.")
        return

    # Feature engineering for the stock price model
    historical_combined_df['target_price'] = historical_combined_df['adjustedCloseStockPrice'].shift(-1)

    for kpi in kpis_to_forecast:
        if kpi in historical_combined_df.columns:
            historical_combined_df[f'lagged_{kpi}'] = historical_combined_df[kpi].shift(1)

    historical_combined_df['lagged_adj_close'] = historical_combined_df['adjustedCloseStockPrice'].shift(1)

    historical_combined_df.dropna(inplace=True)

    features = [f'lagged_{kpi}' for kpi in kpis_to_forecast if f'lagged_{kpi}' in historical_combined_df.columns] + ['lagged_adj_close']
    X = historical_combined_df[features]
    y = historical_combined_df['target_price']

    # Train the XGBoost model on the full historical data
    xgb_model = XGBRegressor(n_estimators=100, random_state=42)
    xgb_model.fit(X, y)

    # Create a DataFrame for future prediction using the forecasted KPIs
    last_historical_row = historical_combined_df.iloc[-1]

    future_data = pd.DataFrame({
        f'lagged_{kpi}': [kpi_forecasts[kpi].iloc[0]] for kpi in kpis_to_forecast if kpi in kpi_forecasts.columns
    })
    future_data['lagged_adj_close'] = [last_historical_row['target_price']]

    predicted_stock_price = xgb_model.predict(future_data)

    # Save the stock price forecast
    forecast_df = pd.DataFrame({
        'Report Date': [kpi_forecasts['Report Date'].iloc[0]],
        'Forecasted Price': predicted_stock_price
    })

    forecast_df.to_csv('price_forecast.csv', index=False)
    print("Stock price forecast saved to 'price_forecast.csv'")

    print("\nAll forecasts are complete.")

if __name__ == "__main__":
    two_stage_forecast()