#!/usr/bin/env python3
"""
Main execution script for NVIDIA Moat Analysis
Orchestrates the entire data pipeline and forecasting process
"""

import logging
from src.data_pipeline.financial_data_collector import fetch_financial_data
from src.data_pipeline.stock_data_collector import fetch_stock_data
from src.data_pipeline.data_processor import process_data
from src.machine_learning.forecasting_engine import run_forecasting
from src.machine_learning.two_stage_forecast import two_stage_forecast

def main():
    """Main execution function"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting NVIDIA Moat Analysis Pipeline")
        
        # Step 1: Data Collection
        logger.info("Step 1: Collecting data...")
        financial_data = fetch_financial_data()
        stock_data = fetch_stock_data()
        
        # Step 2: Data Processing
        logger.info("Step 2: Processing data...")
        processed_data = process_data(financial_data, stock_data)
        
        # Step 3: Forecasting
        logger.info("Step 3: Running forecasts...")
        forecast_results = run_forecasting(processed_data)
        
        # Step 4: Two-Stage Forecasting
        logger.info("Step 4: Running two-stage forecasting...")
        two_stage_results = two_stage_forecast()
        
        logger.info("Pipeline completed successfully!")
        
        return {
            'financial_data': financial_data,
            'stock_data': stock_data,
            'forecast_results': forecast_results,
            'two_stage_results': two_stage_results
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    results = main()