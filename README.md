# SECURESKIES MLAT Telemetry Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/tag/rwiren/hermes-learning?label=Version&color=green)](https://github.com/rwiren/hermes-learning/tags)
[![Status](https://img.shields.io/badge/Status-Development-yellow.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
![Last Updated](https://img.shields.io/github/last-commit/rwiren/hermes-learning?label=Last%20Updated&color=orange)

## Overview
This repository houses an automated end-to-end (E2E) data pipeline designed to scrape, parse, and format ADS-B/MLAT hex telemetry from the SECURESKIES tactical hub (`www.securingskies.eu`). The primary objective is the generation of synthetic trajectory datasets for machine learning applications, specifically addressing tracking anomalies (e.g., IKARUS C-42 Bison/OH-U439 erroneously classified as B4 UAV).

## Learning Vault (Shared Knowledge Base)
The repository includes a dedicated `learning/` workspace for capturing reusable lessons, experiment outcomes, and candidate skills.

Structure:
- `learning/lessons/` — dated lessons learned with evidence
- `learning/experiments/` — concise hypothesis→result logs
- `learning/skills/` — candidate procedures for future skill promotion
- `learning/templates/` — standardized note templates

Rules:
- Record what was learned and how it was learned.
- Link every lesson to issue/branch/commit evidence.
- Never store secrets, tokens, private keys, or personal sensitive data.

## Model Folder Policy (Public Repo Safety)
The `model/` directory is intentionally allowlisted to track only lightweight metadata:
- `model/Modelfile`
- `model/README.md`
- `model/.gitignore`

Large model binaries (e.g., GGUF/weights/checkpoints) and credentials are excluded from version control by policy.

## LLM Benchmark Snapshot (Document-Improvement Workload, 2026-04-17)

This snapshot records observed latency and reliability on this setup for document-improvement style prompts.

### Prompt A (sanity)
`Reply with exactly OK`

### Prompt B (document-improvement style)
`Berylia capability-to-impact matrix: list exactly 3 concise improvements...`

### Results

| Model / Path | Prompt A | Prompt B | Notes |
|---|---:|---:|---|
| `qwen2.5:14b` via `hermes chat` (local) | n/a in this sweep | 71.81s, 52.44s, 55.13s (p50 55.13s, p95 71.81s) | 3/3 success, required sections present, no tool-JSON leakage |
| `qwen2.5-64k:latest` via `hermes chat` (local) | n/a in this sweep | 111.49s, 74.82s, 69.34s (p50 74.82s, p95 111.49s) | 3/3 success, required sections present, no tool-JSON leakage |
| `supergemma4-uncensored` via `hermes chat` (local) | 19.847s, 2.699s | timeout@180s, timeout@180s | Fast warm responses on tiny prompts, unstable on practical doc-improvement workload |
| `gpt-5.3-codex` via Copilot | 11.517s, 10.535s | 26.53s, 47.405s | Consistently successful and fastest for practical doc-improvement prompt shape in this comparison |

Additional check:
- Direct Ollama API responded in ~3.6s for a similar prompt, indicating the observed long-generation bottleneck is in the `hermes chat` local-model path for this workload shape, not endpoint availability.

Operational guidance from this snapshot:
- For local Hermes document-improvement tasks: prefer `qwen2.5:14b` over `qwen2.5-64k:latest` for latency.
- For highest reliability/speed on practical document-improvement prompts in this environment: use Copilot `gpt-5.3-codex`.
- Avoid `supergemma4-uncensored` for longer document-improvement generations until routing/generation-path bottleneck is resolved.

### Recommended command presets

```bash
# 1) Local default (balanced speed/reliability for doc-improvement)
hermes chat -Q -m qwen2.5:14b -q "<your document-improvement prompt>"

# 2) Local long-context override (when context window matters more than latency)
hermes chat -Q -m qwen2.5-64k:latest -q "<your document-improvement prompt>"

# 3) Copilot path (fast/reliable on this workload snapshot)
hermes chat -Q --provider copilot -m gpt-5.3-codex -q "<your document-improvement prompt>"
```

## Pipeline Architecture

The pipeline is structured into four deterministic stages:

### Stage 1: Ingestion (Collection)
* **Target:** SECURESKIES web dashboard / API endpoints.
* **Mechanism:** Headless extraction (via Playwright/BeautifulSoup) targeting heavily nested DOM elements to capture active track arrays.
* **Data Points:** ICAO Hex code, Squawk, Callsign, Latitude, Longitude, Altitude, Ground Speed, and classification flags.

### Stage 2: Processing & Parsing (Transformation)
* **Validation:** Sanity checks on hex formats and coordinate bounds.
* **Correction Logic:** Identification and tagging of known classification anomalies (e.g., cross-referencing Hex `4649e7` to override UAV classifications).
* **Formatting:** Flattening hierarchical payload data into structured, strictly typed records.

### Stage 3: Storage (Load)
* **Format:** Time-series Parquet or append-only CSV.
* **Partitioning:** Data partitioned by date (`YYYY-MM-DD`) and region to optimize downstream batch ML processing.

### Stage 4: Execution Engine (Automation)
* **Scheduling:** CRON-driven daemon executing the ingestion script at defined intervals.
* **Monitoring:** Logging stdout/stderr streams to track extraction failure rates and DOM mutation breaks.

## Development Setup
*Requires Python 3.10+*

1. Clone the repository and checkout `develop`.
2. Install dependencies:
   - `python3 -m pip install -r requirements.txt`
   - `python3 -m pip install playwright`
   - `python3 -m playwright install chromium`
3. Follow branch and commit conventions outlined in `CONTRIBUTING.md`.

## Live SECURESKIES Collection (Stage 1)

Run live ingestion from the tactical hub with configurable duration:

```bash
python3 src/ingestion/scraper.py --minutes 15 --interval 30
```

Output artifacts:
- Raw snapshots: `data/raw/telemetry_snapshots_<run_id>.json`
- Normalized telemetry: `data/raw/telemetry_<run_id>.json`

Important URL constraints for the tactical hub:
- Use exactly `http://www.securingskies.eu:8080/`
- Do not switch to `https://`
- Do not remove `www.`
- Do not omit port `8080`

## Strict Anomaly Evaluation

The strict evaluation run tracks AUROC, AUPRC, Brier score, Precision/Recall/F1,
MCC, Balanced Accuracy, and confusion-matrix counts over repeated seeded runs.

Latest strict-eval outputs:
- `reports/metrics/anomaly_strict_eval_2026-04-16_with_live.csv`
- `reports/metrics/anomaly_strict_eval_summary_2026-04-16_with_live.csv`

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
