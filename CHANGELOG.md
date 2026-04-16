# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-16

### Added
- `src/processing/transformer.py`: Stage 2 data transformation layer mapping raw JSON telemetry to partitioned Parquet formats via `pandas` and `pyarrow`.
- Spatial and cryptographic validation logic enforcing strict Lat/Lon bounds and ICAO Hex formats.
- `requirements.txt` update to include `pandas` and `pyarrow` dependencies.
- `src/ingestion/scraper.py`: Playwright-based MLAT telemetry ingestion script with anomaly correction logic for IKARUS C-42 Bison (Hex: 4649e7).
- `requirements.txt` defining Playwright and BeautifulSoup dependencies.
- `data/raw` directory structure for JSON telemetry output.
- Dynamic repository shields/badges to the top of `README.md`.
- `LICENSE` file establishing MIT License for the project.
- `README.md` defining the end-to-end MLAT telemetry pipeline architecture and data flow.
- `CONTRIBUTING.md` establishing Git workflow, branch protections, and Conventional Commits.
- Initial Git repository scaffolding with `main` and `develop` branches.
- `CHANGELOG.md` to track project evolution.
