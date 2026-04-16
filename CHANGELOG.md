# 📝 Project Changelog

All notable changes to the **hermes-learning** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Pipeline Analytics & Visualization:** Introduced `src/analytics/pipeline_visualizer.py` to generate analytical plots (Storage Growth, Daily Volume) for monitoring pipeline health.
- **Pipeline Orchestration (Stage 4):** Integrated analytics step into `run_pipeline.py` to automate post-processing visualization.
- **Standardized Asset Management:** Created `assets/` structure (`plots`, `images`, `audio`) for managed storage of pipeline artifacts.
- **Analytical Documentation:** Introduced `docs/analysis/` directory with a structured `pipeline_audit_template.md` for formal pipeline performance audits.
- **Dependency Robustness:** Updated `requirements.txt` with `seaborn` and `pyarrow` to support advanced analytics and Parquet operations.
- **ML Environment Setup:** Updated `requirements.txt` with `torch`, `torch-geometric`, and `mamba-ssm`.
- **Data Preparation for Anomaly Detection:** Implemented `src/features/anomaly_prep.py` to load and prepare telemetry data for anomaly detection models.
- **Foundational GNN Anomaly Detector:** Implemented `src/analytics/anomaly_detection/gnn_detector.py` for spatial anomaly detection using a simple GNN model.
- **Foundational DeepSeek MCHC Anomaly Detector:** Implemented `src/analytics/anomaly_detection/mchc_detector.py` for ghost aircraft detection with a placeholder MCHC model.
- **Mamba SSM Anomaly Detector:** Implemented `src/analytics/anomaly_detection/mamba_detector.py` for drift attack detection and long-context trajectory tracking.
- **xLSTM Anomaly Detector:** Implemented `src/analytics/anomaly_detection/xlstm_detector.py` for rapid maneuver anomaly detection.
- **Initial Anomaly Detection Evaluation Script:** Implemented `src/analytics/anomaly_evaluation.py` to provide a foundational framework for evaluating anomaly detection models.
- **Stability Fixes:** Fixed import/runtime issues in `gnn_detector.py`, `mamba_detector.py`, and `anomaly_evaluation.py` and validated successful execution of the initial anomaly evaluation pipeline.
- **Model Benchmark Pipeline:** Added `src/analytics/model_benchmark_pipeline.py` for unified train/test/validate/compare workflow across anomaly and trajectory models with automatic metric export and plot generation.
- **Trajectory Predictors:** Added `src/models/trajectory_prediction/mamba_predictor.py` and `src/models/trajectory_prediction/xlstm_predictor.py` for baseline trajectory benchmarking integration.
- **Benchmark Dependencies:** Added `scikit-learn` and `matplotlib` to support metrics computation and performance visualization.













## [0.12.0] - 2026-04-16: The "Automation" Update
**Feature Release: Stage 4 Data Pipeline Automation.**

### ⚙️ Data Pipeline
*   **Automation Orchestrator:** Implemented `run_pipeline.py` to automate the execution of the Stage 2 (Transformation) and Stage 3 (Storage) data pipeline.
*   **Workflow Integration:** The master script is designed for easy integration into automation frameworks like cron jobs or GitHub Actions.
*   **Robust Logging:** Integrated comprehensive logging to `pipeline.log` for improved debugging and pipeline monitoring.

---

## [0.11.0] - 2026-04-16: The "Data Lake" Update
**Feature Release: Stage 3 Data Storage Solution.**

### ⚙️ Data Pipeline
*   **Storage Management Layer:** Implemented `src/storage/storage_manager.py` to move processed telemetry from `data/processed` into a dedicated `data/storage` local data lake.
*   **Partition Preservation:** The storage manager maintains the date-based partitioning (`YYYY-MM-DD`) established in Stage 2.
*   **Automated Transfer:** Includes logic to automatically transfer files and clean up empty source directories.

---

## [0.10.0] - 2026-04-16: The "Telemetry Transformation" Update
**Feature Release: Stage 2 Data Transformation & Processing Pipeline.**

### ⚙️ Data Pipeline
*   **Telemetry Transformation Layer:** Implemented `src/processing/transformer.py` to process raw JSON telemetry into strictly typed, ML-ready datasets.
*   **Validation Layer:** Enforces strict sanity checks on ICAO Hex formats (6-character hex strings) and spatial coordinate bounds (Latitude -90 to 90, Longitude -180 to 180).
*   **Data Transformation:** Flattens hierarchical JSON payloads into standardized tabular records.
*   **Storage & Partitioning:** Converts and loads sanitized data into time-series Parquet format (with CSV fallback) optimized for batch ML workloads, partitioned by date (YYYY-MM-DD).
*   **Metadata Integration:** Seamlessly incorporates Stage 1 `anomaly_corrected` metadata flags into the final ML schema.
