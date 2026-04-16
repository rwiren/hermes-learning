#!/usr/bin/env python3
"""
Module: transformer.py
Description: Stage 2 Transformation layer for the SECURESKIES MLAT Telemetry Pipeline.
Author: Hermes
License: MIT

This module processes raw JSON telemetry payloads extracted during Stage 1. 
It enforces strict validation bounds (coordinate sanity, hex integrity), flattens 
the payloads into tabular structures, and encodes the curated data into time-series 
Parquet formats partitioned by date for optimized downstream machine learning ingestion.
"""

import json
import logging
import re
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z"
)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
HEX_PATTERN = re.compile(r"^[0-9a-fA-F]{6}$")

def validate_telemetry(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies spatial and cryptographic validation constraints to the telemetry dataframe.
    Drops rows that violate basic physics or formatting rules.
    """
    initial_count = len(df)
    
    # Validation 1: ICAO Hex formatting (6 char hex)
    valid_hex = df['hex'].astype(str).str.match(HEX_PATTERN)
    
    # Validation 2: Spatial coordinate bounds
    valid_lat = df['lat'].between(-90.0, 90.0)
    valid_lon = df['lon'].between(-180.0, 180.0)
    
    # Validation 3: Altitude physics (Allowing up to 100k feet for extreme tracks)
    valid_alt = df['alt'].between(-2000, 100000)
    
    # Combine masks
    clean_df = df[valid_hex & valid_lat & valid_lon & valid_alt].copy()
    
    dropped = initial_count - len(clean_df)
    if dropped > 0:
        logger.warning(f"Validation pruned {dropped} malformed telemetry records.")
        
    return clean_df

def process_raw_files():
    """
    Scans the raw directory for unprocessed JSON telemetry, transforms them, 
    and writes to partitioned Parquet files.
    """
    if not RAW_DIR.exists():
        logger.error(f"Raw data directory missing at {RAW_DIR}")
        return

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw_files = list(RAW_DIR.glob("telemetry_*.json"))
    
    if not raw_files:
        logger.info("No raw telemetry files found for processing.")
        return

    frames = []
    processed_count = 0

    for file_path in raw_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not data:
                    continue
                
                df = pd.json_normalize(data)
                
                # Assign processing timestamp for time-series integrity
                df['processed_at'] = datetime.now(timezone.utc)
                
                # Create partitioning key (YYYY-MM-DD) based on processing time
                # In a live system, this would use the track's native timestamp
                df['partition_date'] = df['processed_at'].dt.strftime('%Y-%m-%d')
                
                frames.append(df)
                processed_count += 1
                
                # Rename the processed file to avoid duplicate ingestion
                file_path.rename(file_path.with_suffix('.json.processed'))
                
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")

    if frames:
        master_df = pd.concat(frames, ignore_index=True)
        master_df = validate_telemetry(master_df)
        
        if not master_df.empty:
            # Write out to Parquet partitioned by date
            output_path = PROCESSED_DIR / "telemetry_dataset"
            logger.info(f"Writing {len(master_df)} verified records to {output_path} (Parquet)")
            
            master_df.to_parquet(
                output_path, 
                engine='pyarrow',
                partition_cols=['partition_date'],
                index=False,
                compression='snappy'
            )
            logger.info("Stage 2 processing complete.")
        else:
            logger.warning("All records dropped during validation.")

def main():
    logger.info("Starting Stage 2: Telemetry Transformation Pipeline")
    process_raw_files()

if __name__ == "__main__":
    main()
