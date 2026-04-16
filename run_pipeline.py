"""
run_pipeline.py

This script serves as the master automation orchestrator for the ADS-B data pipeline.
It automates the execution of Stage 2 (Transformation) and Stage 3 (Storage) to create
a seamless, end-to-end workflow.

The pipeline is executed as follows:
1.  **Stage 2: Transformation:** The `TelemetryTransformer` is invoked to process
    raw JSON telemetry from `data/raw` into validated, partitioned Parquet files
    in `data/processed`.
2.  **Stage 3: Storage:** The `StorageManager` is invoked to move the processed
    Parquet files from `data/processed` into the `data/storage` data lake.

This script includes robust error handling and logging to ensure reliability and
facilitate debugging.
"""

import logging
from src.processing.transformer import TelemetryTransformer
from src.storage.storage_manager import StorageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

def main():
    """
    Main function to orchestrate the data pipeline execution.
    """
    logging.info("Starting ADS-B data pipeline...")

    try:
        # Stage 2: Transformation
        logging.info("--- Stage 2: Telemetry Transformation ---")
        transformer = TelemetryTransformer()
        transformer.process_raw_files()
        logging.info("--- Stage 2: Transformation complete. ---")

        # Stage 3: Storage
        logging.info("--- Stage 3: Data Storage ---")
        storage_manager = StorageManager()
        storage_manager.move_processed_to_storage()
        logging.info("--- Stage 3: Storage complete. ---")

        logging.info("ADS-B data pipeline finished successfully.")

    except Exception as e:
        logging.error(f"An error occurred during pipeline execution: {e}", exc_info=True)
        # Depending on requirements, could add alerting (e.g., email, Slack) here.

if __name__ == "__main__":
    main()
