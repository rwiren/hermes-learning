# SECURESKIES MLAT Telemetry Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/tag/rwiren/hermes-learning?label=Version&color=green)](https://github.com/rwiren/hermes-learning/tags)
[![Status](https://img.shields.io/badge/Status-Development-yellow.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
![Last Updated](https://img.shields.io/github/last-commit/rwiren/hermes-learning?label=Last%20Updated&color=orange)

## Overview
This repository houses an automated end-to-end (E2E) data pipeline designed to scrape, parse, and format ADS-B/MLAT hex telemetry from the SECURESKIES tactical hub (`www.securingskies.eu`). The primary objective is the generation of synthetic trajectory datasets for machine learning applications, specifically addressing tracking anomalies (e.g., IKARUS C-42 Bison/OH-U439 erroneously classified as B4 UAV).

## Pipeline Architecture

The pipeline is structured into four deterministic stages:

### Stage 1: Ingestion (Collection)
*   **Target:** SECURESKIES web dashboard / API endpoints.
*   **Mechanism:** Headless extraction (via Playwright/BeautifulSoup) targeting heavily nested DOM elements to capture active track arrays.
*   **Data Points:** ICAO Hex code, Squawk, Callsign, Latitude, Longitude, Altitude, Ground Speed, and classification flags.

### Stage 2: Processing & Parsing (Transformation)
*   **Validation:** Sanity checks on hex formats and coordinate bounds.
*   **Correction Logic:** Identification and tagging of known classification anomalies (e.g., cross-referencing Hex `4649e7` to override UAV classifications).
*   **Formatting:** Flattening hierarchical payload data into structured, strictly typed records.

### Stage 3: Storage (Load)
*   **Format:** Time-series Parquet or append-only CSV.
*   **Partitioning:** Data partitioned by date (`YYYY-MM-DD`) and region to optimize downstream batch ML processing.

### Stage 4: Execution Engine (Automation)
*   **Scheduling:** CRON-driven daemon executing the ingestion script at defined intervals.
*   **Monitoring:** Logging stdout/stderr streams to track extraction failure rates and DOM mutation breaks.

## Development Setup
*Requires Python 3.10+*

1. Clone the repository and checkout `develop`.
2. Install dependencies (TBD: `requirements.txt` / `pyproject.toml`).
3. Follow branch and commit conventions outlined in `CONTRIBUTING.md`.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
