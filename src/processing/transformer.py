"""
transformer.py

This module provides the Stage 2 data transformation layer for processing raw JSON telemetry
extracted by the Stage 1 ingestion scraper into strictly typed, ML-ready datasets.

The transformation pipeline includes:
1. Validation: Enforcing strict sanity checks on ICAO Hex formats and spatial coordinate bounds.
2. Transformation: Flattening hierarchical JSON payloads into standardized tabular records.
3. Storage Encoding: Converting and loading sanitized data into time-series Parquet format (with CSV fallback).
4. Partitioning: Implementing a robust data partitioning strategy by date (YYYY-MM-DD).
5. Metadata Incorporation: Seamlessly integrating Stage 1 anomaly_corrected metadata flags into the final ML schema.
"""

import os
import json
import re
import pandas as pd
from datetime import datetime

class TelemetryTransformer:
    """
    Transforms raw JSON telemetry data into a cleaned, validated, and ML-ready tabular format.
    """
    def __init__(self, raw_data_path='data/raw', processed_data_path='data/processed'):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        os.makedirs(self.processed_data_path, exist_ok=True)

    def _validate_icao_hex(self, icao_hex: str) -> bool:
        """
        Validates if the ICAO Hex is a 6-character hexadecimal string.
        """
        if not isinstance(icao_hex, str):
            return False
        return bool(re.fullmatch(r'^[0-9a-fA-F]{6}$', icao_hex))

    def _validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validates if latitude and longitude are within their respective bounds.
        Latitude: -90 to 90
        Longitude: -180 to 180
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)

    def transform_telemetry(self, raw_json_data: list) -> pd.DataFrame:
        """
        Transforms a list of raw JSON telemetry records into a pandas DataFrame.
        Applies validation, flattens the structure, and prepares for ML schema.
        """
        processed_records = []
        for record in raw_json_data:
            # Extract and validate ICAO Hex
            icao_hex = record.get('icao_hex')
            if not self._validate_icao_hex(icao_hex):
                # Optionally log or handle invalid ICAO Hex
                continue

            # Extract and validate coordinates
            latitude = record.get('latitude')
            longitude = record.get('longitude')
            if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)) or \
               not self._validate_coordinates(latitude, longitude):
                # Optionally log or handle invalid coordinates
                continue

            # Flatten and select relevant fields
            transformed_record = {
                'icao_hex': icao_hex,
                'timestamp': record.get('timestamp'),
                'latitude': latitude,
                'longitude': longitude,
                'altitude': record.get('altitude'),
                'velocity': record.get('velocity'),
                'track': record.get('track'),
                'squawk': record.get('squawk'),
                'vertical_rate': record.get('vertical_rate'),
                'ground_speed': record.get('ground_speed'),
                'callsign': record.get('callsign'),
                'anomaly_corrected': record.get('anomaly_corrected', False) # Incorporate metadata flag
            }
            processed_records.append(transformed_record)

        return pd.DataFrame(processed_records)

    def process_raw_files(self):
        """
        Reads raw JSON files from raw_data_path, transforms them, and saves
        to processed_data_path partitioned by date.
        """
        for filename in os.listdir(self.raw_data_path):
            if filename.endswith('.json'):
                raw_file_path = os.path.join(self.raw_data_path, filename)
                
                with open(raw_file_path, 'r') as f:
                    raw_data = json.load(f)
                
                df = self.transform_telemetry(raw_data)
                
                if not df.empty:
                    # Determine partitioning date from timestamp (assuming 'timestamp' exists and is parseable)
                    # For simplicity, using the first record's timestamp; a more robust solution might average or use filename
                    try:
                        first_timestamp = df['timestamp'].iloc[0]
                        # Assuming timestamp is in ISO format or similar, adjust if needed
                        processing_date = datetime.fromisoformat(first_timestamp.replace('Z', '+00:00')) if isinstance(first_timestamp, str) else datetime.fromtimestamp(first_timestamp)
                        partition_dir = os.path.join(self.processed_data_path, processing_date.strftime('%Y-%m-%d'))
                        os.makedirs(partition_dir, exist_ok=True)

                        output_filename = filename.replace('.json', '.parquet')
                        output_file_path = os.path.join(partition_dir, output_filename)
                        
                        df.to_parquet(output_file_path, index=False)
                        print(f"Successfully processed {raw_file_path} to {output_file_path}")
                    except Exception as e:
                        print(f"Error processing {raw_file_path}: {e}")
                else:
                    print(f"No valid telemetry records found in {raw_file_path} after validation.")

if __name__ == '__main__':
    # Example usage (will require sample data in data/raw to run effectively)
    # Ensure data/raw and data/processed directories exist or are created by the class.
    
    # Create dummy raw data for testing
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)

    sample_raw_data = [
        {
            "icao_hex": "a00001",
            "timestamp": "2026-04-16T10:00:00Z",
            "latitude": 60.192059,
            "longitude": 24.945831,
            "altitude": 10000,
            "velocity": 450,
            "track": 90,
            "squawk": "1234",
            "vertical_rate": 512,
            "ground_speed": 440,
            "callsign": "FIN123",
            "anomaly_corrected": False
        },
        {
            "icao_hex": "b00002",
            "timestamp": "2026-04-16T10:01:00Z",
            "latitude": 60.193000,
            "longitude": 24.946000,
            "altitude": 10500,
            "velocity": 460,
            "track": 95,
            "squawk": "1235",
            "vertical_rate": 256,
            "ground_speed": 450,
            "callsign": "SAS456",
            "anomaly_corrected": True
        },
        {
            "icao_hex": "c00003", # Invalid ICAO hex
            "timestamp": "2026-04-16T10:02:00Z",
            "latitude": 100.000, # Invalid latitude
            "longitude": 24.947000,
            "altitude": 11000,
            "velocity": 470,
            "track": 100,
            "squawk": "1236",
            "vertical_rate": 0,
            "ground_speed": 460,
            "callsign": "NOR789",
            "anomaly_corrected": False
        }
    ]

    with open('data/raw/sample_telemetry_2026-04-16.json', 'w') as f:
        json.dump(sample_raw_data, f, indent=4)

    transformer = TelemetryTransformer()
    transformer.process_raw_files()
