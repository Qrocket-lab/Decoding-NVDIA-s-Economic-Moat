import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score

def run_forecasting_model():
    """
    Loads, preprocesses, and models financial data to forecast stock prices
    using multiple machine learning models.
    """
    # --- 1. Load and Prepare Data ---
    print("Step 1: Loading and preparing data...")
    try:
        # Load the quarterly financial data
        financial_df = pd.read_csv('nvidia_financial_data_DAX.csv')

        # --- Debugging: Print columns after loading ---
        print("\nColumns in financial_df after loading:")
        print(financial_df.columns.tolist())
        print("-" * 30)
        # --- End Debugging ---

        # Clean column names (remove leading/trailing spaces)
        financial_df.columns = financial_df.columns.str.strip()

        # Create 'Report Date' from 'Year' and 'Quarter' columns in financial_df
        print("Creating 'Report Date' from 'Year' and 'Quarter' columns in financial data...")
        # Map quarter to a month to create a valid date (assuming quarter ends on the last day of the 3rd, 6th, 9th, 12th month)
        quarter_to_month_day = {1: '03-31', 2: '06-30', 3: '09-30', 4: '12-31'}

        # --- Corrected logic to handle potential 'Qtr' in Quarter and missing Year/Quarter ---
        # Ensure 'Year' and 'Quarter' columns exist before accessing them
        if 'Year' not in financial_df.columns or 'Quarter' not in financial_df.columns:
             raise KeyError("Missing 'Year' or 'Quarter' column in financial data.")

        # Ensure Year and Quarter are treated as strings before concatenation
        financial_df['Quarter'] = financial_df['Quarter'].astype(str).str.replace('Qtr ', '')
        # Convert Quarter to numeric, coercing errors to NaN
        financial_df['Quarter_num'] = pd.to_numeric(financial_df['Quarter'], errors='coerce')

        # Drop rows where Quarter could not be converted to numeric
        financial_df.dropna(subset=['Year', 'Quarter_num'], inplace=True)
        financial_df['Quarter_num'] = financial_df['Quarter_num'].astype(int) # Convert to int after dropping NaNs


        financial_df['Report Date'] = financial_df['Year'].astype(str) + '-' + financial_df['Quarter_num'].map(quarter_to_month_day).astype(str)
        financial_df['Report Date'] = pd.to_datetime(financial_df['Report Date'], errors='coerce')

        # Remove rows with invalid dates (NaT)
        financial_df.dropna(subset=['Report Date'], inplace=True)
        financial_df.sort_values('Report Date', inplace=True)

        # Load the daily stock price data (User-provided CSV)
        stock_df = pd.read_csv('nvda_stock_data.csv')
        # Ensure 'Report Date' is datetime and sort
        stock_df['Report Date'] = pd.to_datetime(stock_df['Report Date'])
        # Sort by 'Report Date'
        stock_df.sort_values('Report Date', inplace=True)

        # Merge datasets by finding the stock price closest to each report date
        combined_df = pd.merge_asof(
            financial_df, # financial_df now has 'Report Date' and is sorted
            stock_df[['Report Date', 'adjustedCloseStockPrice']],
            left_on='Report Date',
            right_on='Report Date',
            direction='nearest',
            suffixes=('', '_stock')
        )

        # Clean percentage columns and convert to numeric
        percentage_cols = ['ROIC (%)', 'Gross Margin %', 'R&D as % of Revenue']
        for col in percentage_cols:
            if col in combined_df.columns:
                combined_df[col] = combined_df[col].astype(str).str.replace('%', '').replace('', np.nan)
                combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

        # Ensure Free Cash Flow is numeric
        if 'Free Cash Flow' in combined_df.columns:
            combined_df['Free Cash Flow'] = pd.to_numeric(combined_df['Free Cash Flow'], errors='coerce')


        # Drop rows with any missing values for now to simplify the model
        # Ensure the KPI columns exist before dropping NaNs
        kpis_to_check = percentage_cols + ['Free Cash Flow'] # Use the cleaned list
        columns_to_check = ['adjustedCloseStockPrice'] + [kpi for kpi in kpis_to_check if kpi in combined_df.columns]

        # Drop rows where any of the essential columns (including selected KPIs) are missing
        combined_df.dropna(subset=columns_to_check, inplace=True)


    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure both 'nvidia_financial_data_DAX.csv' and 'nvda_stock_data.csv' are in the same folder.")
        return
    except KeyError as e:
        print(f"Error: Missing expected column in one of the dataframes: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred during data loading or preparation: {e}")
        return


    # --- 2. Feature Engineering ---
    print("Step 2: Creating new features...")
    # Target variable (what we want to predict)
    combined_df['target_price'] = combined_df['adjustedCloseStockPrice'].shift(-1)

    # Create lagged features for key KPIs and the stock price
    # Ensure the KPI columns exist before creating lagged features
    features = []
    kpis_to_lag = percentage_cols + ['Free Cash Flow'] # Use the cleaned list
    for kpi in kpis_to_lag:
        if kpi in combined_df.columns:
            combined_df[f'lagged_{kpi}'] = combined_df[kpi].shift(1)
            features.append(f'lagged_{kpi}')

    combined_df['lagged_adj_close'] = combined_df['adjustedCloseStockPrice'].shift(1)
    features.append('lagged_adj_close')

    # Drop rows with any NaN after creating lagged features and the target variable
    combined_df.dropna(subset=features + ['target_price'], inplace=True)


    # --- 3. Define Features (X) and Target (y) ---
    # Ensure the feature columns exist in the DataFrame before selecting them
    X = combined_df[features]
    y = combined_df['target_price']

    # Check if there's enough data after dropping NaNs to split
    if len(X) < 2:
        print("Error: Not enough data points remaining after cleaning to train the model.")
        return


    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- 4. Train and Evaluate Models ---
    print("Step 3: Training and evaluating models...")
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, random_state=42)
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        results[name] = {'MAE': mae, 'R-squared': r2}

    print("\nModel Performance Results:")
    for name, metrics in results.items():
        print(f"--- {name} ---")
        print(f"  Mean Absolute Error (MAE): ${metrics['MAE']:.2f}")
        print(f"  R-squared: {metrics['R-squared']:.2f}")

    # --- 5. Generate and Save a Sample Forecast ---
    print("\nStep 4: Generating and saving a sample forecast...")
    # Use the last available data point to make a prediction
    # Ensure there is a last data point before attempting to forecast
    if not X.empty:
        last_data_point = X.tail(1)

        # Use the best-performing model to make a simple forecast
        # For this example, let's assume XGBoost is the best
        best_model = XGBRegressor(n_estimators=100, random_state=42)
        best_model.fit(X, y) # Train on full dataset

        predicted_price = best_model.predict(last_data_point)

        # Create a DataFrame for the forecast to be used in Power BI
        # Use the date of the last data point + an appropriate time offset (e.g., 3 months for quarterly)
        forecast_date = combined_df['Report Date'].iloc[-1] + pd.DateOffset(months=3)

        forecast_df = pd.DataFrame({
            'Report Date': [forecast_date.date()], # Convert to date object for consistency
            'Forecasted Price': predicted_price
        })

        forecast_df.to_csv('price_forecast.csv', index=False)
        print("Forecast successfully saved to 'price_forecast.csv'")
    else:
        print("Could not generate forecast as there is no data to predict from.")


if __name__ == "__main__":
    run_forecasting_model()