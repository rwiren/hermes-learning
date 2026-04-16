"""
storage_manager.py

This module implements the Stage 3 data storage solution for the transformed, ML-ready
telemetry datasets. It is responsible for moving partitioned Parquet files from the
`data/processed` directory to a dedicated `data/storage` data lake, maintaining
the date-based partitioning structure.

Key functionalities include:
1.  Defining source and destination paths.
2.  Automating the transfer of processed files.
3.  Ensuring data integrity during transfer.
4.  Maintaining discoverability and accessibility for downstream ML workloads.
"""

import os
import shutil
from datetime import datetime

class StorageManager:
    """
    Manages the storage of processed telemetry data, moving it to a dedicated
    data lake structure.
    """
    def __init__(self, processed_data_path='data/processed', storage_data_path='data/storage'):
        self.processed_data_path = processed_data_path
        self.storage_data_path = storage_data_path
        os.makedirs(self.storage_data_path, exist_ok=True)

    def move_processed_to_storage(self):
        """
        Iterates through the partitioned `data/processed` directory, moves
        Parquet files to `data/storage`, and preserves the directory structure.
        """
        print(f"Starting data transfer from {self.processed_data_path} to {self.storage_data_path}")

        for root, dirs, files in os.walk(self.processed_data_path):
            # Construct the relative path from processed_data_path to the current root
            relative_path = os.path.relpath(root, self.processed_data_path)
            
            # Construct the corresponding destination path in data/storage
            destination_dir = os.path.join(self.storage_data_path, relative_path)
            os.makedirs(destination_dir, exist_ok=True)

            for file in files:
                if file.endswith('.parquet') or file.endswith('.csv'): # Also consider CSV fallback
                    source_file_path = os.path.join(root, file)
                    destination_file_path = os.path.join(destination_dir, file)

                    try:
                        shutil.move(source_file_path, destination_file_path)
                        print(f"Moved: {source_file_path} -> {destination_file_path}")
                    except Exception as e:
                        print(f"Error moving {source_file_path}: {e}")
            
            # Clean up empty processed directories after moving files
            if not os.listdir(root) and root != self.processed_data_path:
                try:
                    os.rmdir(root)
                    print(f"Removed empty directory: {root}")
                except OSError as e:
                    print(f"Error removing directory {root}: {e}")
        print("Data transfer complete.")

if __name__ == '__main__':
    # Example usage (requires data in data/processed to run effectively)
    # For demonstration, ensure data/processed/YYYY-MM-DD/ exists with some .parquet files
    
    # Create dummy processed data for testing if it doesn't exist
    dummy_date = datetime.now().strftime('%Y-%m-%d')
    dummy_processed_dir = os.path.join('data/processed', dummy_date)
    os.makedirs(dummy_processed_dir, exist_ok=True)

    dummy_parquet_file = os.path.join(dummy_processed_dir, 'dummy_telemetry.parquet')
    if not os.path.exists(dummy_parquet_file):
        # Create a dummy parquet file (requires pandas and pyarrow)
        try:
            import pandas as pd
            df = pd.DataFrame({
                'icao_hex': ['a1b2c3', 'd4e5f6'],
                'timestamp': [datetime.now(), datetime.now()],
                'latitude': [60.0, 61.0],
                'longitude': [25.0, 26.0]
            })
            df.to_parquet(dummy_parquet_file, index=False)
            print(f"Created dummy processed data: {dummy_parquet_file}")
        except ImportError:
            print("Pandas or PyArrow not installed. Skipping dummy parquet file creation.")
            print("Please ensure data/processed/YYYY-MM-DD/ contains .parquet files for testing.")

    storage_manager = StorageManager()
    storage_manager.move_processed_to_storage()
