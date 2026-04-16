#!/usr/bin/env python3
"""
Module: scraper.py
Description: Stage 1 Ingestion layer for the SECURESKIES MLAT Telemetry Pipeline.
Author: Hermes
License: MIT

This module performs live telemetry extraction from the SECURESKIES tactical hub
and writes normalized records for downstream Stage 2 transformation.

Design notes:
- Uses Playwright to access dynamic `window.lastMapData` payloads.
- Collects repeated snapshots over a configurable duration.
- Persists both raw snapshots (JSON) and normalized records (JSON list).
- Flags anomaly labels using dashboard signals (uav/spoof/anomaly_score) for
  strict-evaluation dataset generation.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
)
logger = logging.getLogger(__name__)

# Critical URL constraints validated for this dashboard
TARGET_URL = "http://www.securingskies.eu:8080/"
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"

# Known classification overrides retained from prior logic
ANOMALY_REGISTRY = {
    "4649e7": {
        "corrected_classification": "Manned/Fixed-Wing",
        "notes": "IKARUS C-42 Bison (OH-U439) override",
    }
}


def to_float(value: Any, default: float = 0.0) -> float:
    """Safe float conversion with ground-level altitude normalization."""
    try:
        if value is None:
            return default
        if isinstance(value, str) and value.strip().lower() == "ground":
            return 0.0
        return float(value)
    except Exception:
        return default


def initialize_storage(run_id: str) -> Dict[str, Path]:
    """Ensure raw storage directory exists and return output paths."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return {
        "normalized": DATA_DIR / f"telemetry_{run_id}.json",
        "snapshots": DATA_DIR / f"telemetry_snapshots_{run_id}.json",
    }


def apply_anomaly_corrections(track: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply known data purity overrides and attach anomaly metadata.
    """
    hex_code = (track.get("icao_hex") or "").lower()
    if hex_code in ANOMALY_REGISTRY:
        logger.info("Anomaly registry hit for hex=%s; applying correction", hex_code)
        track["classification"] = ANOMALY_REGISTRY[hex_code]["corrected_classification"]
        track["anomaly_corrected"] = True
        track["correction_note"] = ANOMALY_REGISTRY[hex_code]["notes"]
    else:
        # Keep existing boolean if pre-labeled by dashboard logic
        track["anomaly_corrected"] = bool(track.get("anomaly_corrected", False))
    return track


def build_normalized_record(ts_iso: str, aircraft: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize one aircraft record into Stage 2-compatible schema.
    """
    spoof_flags = aircraft.get("spoof_flags") or []
    spoof_score = to_float(aircraft.get("spoof_score"), 0.0)
    dashboard_anom = to_float(aircraft.get("anomaly_score"), 0.0)
    is_uav = bool(aircraft.get("uav", False))

    # Dashboard-derived positive label for strict anomaly evaluation datasets
    dashboard_flag = is_uav or spoof_score > 0 or len(spoof_flags) > 0 or dashboard_anom > 0

    rec = {
        "timestamp": ts_iso,
        "icao_hex": (aircraft.get("hex") or "").lower(),
        "latitude": to_float(aircraft.get("lat"), 0.0),
        "longitude": to_float(aircraft.get("lon"), 0.0),
        "altitude": to_float(aircraft.get("alt"), 0.0),
        "velocity": to_float(aircraft.get("gs"), 0.0),
        "track": to_float(aircraft.get("track"), 0.0),
        "squawk": aircraft.get("squawk"),
        "vertical_rate": 0.0,
        "ground_speed": to_float(aircraft.get("gs"), 0.0),
        "callsign": aircraft.get("flight"),
        "classification": "UAV" if is_uav else "Unknown",
        "anomaly_corrected": bool(dashboard_flag),
        "label_reason": "uav_or_spoof_or_dashboard_anomaly" if dashboard_flag else "none",
        "spoof_score": spoof_score,
        "spoof_flags": spoof_flags,
        "uav": is_uav,
    }
    return apply_anomaly_corrections(rec)


def extract_telemetry(duration_seconds: int = 60, interval_seconds: int = 10) -> Dict[str, List[Dict[str, Any]]]:
    """
    Execute live extraction from SECURESKIES dashboard.

    Returns:
      {
        "snapshots": [ ... raw snapshot payloads ... ],
        "records":   [ ... normalized record list ... ]
      }
    """
    logger.info(
        "Starting live extraction target=%s duration=%ss interval=%ss",
        TARGET_URL,
        duration_seconds,
        interval_seconds,
    )

    start = time.time()
    end = start + duration_seconds
    snapshots: List[Dict[str, Any]] = []
    normalized: List[Dict[str, Any]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            page.goto(TARGET_URL, timeout=60000, wait_until="networkidle")
            time.sleep(3)

            while time.time() < end:
                ts_iso = datetime.now(timezone.utc).isoformat()
                payload = page.evaluate(
                    """() => {
                        const d = window.lastMapData || {};
                        return {
                          sync: d.sync || null,
                          jamming: d.jamming || null,
                          aircraft: (d.aircraft || []).map(a => ({
                            hex: a.hex ?? null,
                            flight: a.flight ?? null,
                            lat: a.lat ?? null,
                            lon: a.lon ?? null,
                            alt: a.alt ?? null,
                            gs: a.gs ?? null,
                            track: a.track ?? null,
                            squawk: a.squawk ?? null,
                            uav: !!a.uav,
                            spoof_score: a.spoof_score ?? 0,
                            spoof_flags: Array.isArray(a.spoof_flags) ? a.spoof_flags : [],
                            anomaly_score: a.anomaly_score ?? null
                          }))
                        };
                    }"""
                )

                aircraft = payload.get("aircraft") or []
                snapshots.append({"timestamp": ts_iso, "payload": payload})

                for a in aircraft:
                    normalized.append(build_normalized_record(ts_iso, a))

                logger.info("Snapshot collected: aircraft=%d total_records=%d", len(aircraft), len(normalized))
                time.sleep(interval_seconds)

        except PlaywrightTimeout:
            logger.error("Timeout while loading SECURESKIES dashboard")
        except Exception as exc:
            logger.error("Unexpected extraction error: %s", exc, exc_info=True)
        finally:
            browser.close()

    return {"snapshots": snapshots, "records": normalized}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live SECURESKIES telemetry scraper")
    parser.add_argument("--minutes", type=int, default=1, help="Collection duration in minutes")
    parser.add_argument("--interval", type=int, default=10, help="Snapshot interval in seconds")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    duration_seconds = max(1, args.minutes) * 60
    interval_seconds = max(1, args.interval)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    outputs = initialize_storage(run_id)

    logger.info("Starting MLAT telemetry ingestion run_id=%s", run_id)
    result = extract_telemetry(duration_seconds=duration_seconds, interval_seconds=interval_seconds)

    with open(outputs["snapshots"], "w", encoding="utf-8") as f:
        json.dump(result["snapshots"], f, indent=2)

    with open(outputs["normalized"], "w", encoding="utf-8") as f:
        json.dump(result["records"], f, indent=2)

    total = len(result["records"])
    positives = sum(1 for r in result["records"] if bool(r.get("anomaly_corrected")))
    negatives = total - positives

    logger.info("Raw snapshots written: %s", outputs["snapshots"])
    logger.info("Normalized telemetry written: %s", outputs["normalized"])
    logger.info("Collection summary: records=%d positives=%d negatives=%d", total, positives, negatives)


if __name__ == "__main__":
    main()
