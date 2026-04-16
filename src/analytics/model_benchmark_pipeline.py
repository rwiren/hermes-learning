import os
from dataclasses import dataclass
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.features.anomaly_prep import AnomalyPreprocessor
from src.analytics.anomaly_detection.gnn_detector import GNNDetector
from src.analytics.anomaly_detection.mchc_detector import MCHCDectector
from src.analytics.anomaly_detection.mamba_detector import MambaDetector
from src.analytics.anomaly_detection.xlstm_detector import XLSTMDetector
from src.models.trajectory_prediction.mamba_predictor import MambaTrajectoryPredictor
from src.models.trajectory_prediction.xlstm_predictor import XLSTMTrajectoryPredictor


@dataclass
class BenchmarkResult:
    model: str
    task: str
    metric_name: str
    metric_value: float


def _load_data_for_date(date: str) -> pd.DataFrame:
    file_path = os.path.join("data", "storage", date, f"sample_telemetry_{date}.parquet")
    if not os.path.exists(file_path):
        return pd.DataFrame()
    return pd.read_parquet(file_path)


def _anomaly_metrics(df: pd.DataFrame):
    if "anomaly_corrected" not in df.columns:
        return None
    y_true = df["anomaly_corrected"].astype(int).values
    if y_true.sum() == 0:
        return None
    return y_true


def run_benchmark(date: str):
    os.makedirs("reports/metrics", exist_ok=True)
    os.makedirs("reports/plots", exist_ok=True)

    pre = AnomalyPreprocessor()
    features_df = pre.prepare_data(date)
    raw_df = _load_data_for_date(date)

    if features_df.empty or raw_df.empty:
        raise RuntimeError(f"No benchmarkable data found for {date}")

    results = []

    # ---------- Anomaly models ----------
    anomaly_ground_truth = _anomaly_metrics(raw_df)

    gnn = GNNDetector(sensor_locations={"north": (60.19, 24.94), "west": (60.20, 24.80), "east": (60.10, 25.10)}, num_features=features_df.shape[1])
    gnn_out = gnn.detect_anomalies(features_df.copy())

    mchc = MCHCDectector(num_node_features=features_df.shape[1])
    mchc_out = mchc.detect_anomalies(features_df.copy())

    mamba = MambaDetector(d_model=features_df.shape[1], sequence_length=2)
    mamba_out = mamba.detect_anomalies(features_df.copy())

    xlstm = XLSTMDetector(input_size=features_df.shape[1], sequence_length=2)
    xlstm_out = xlstm.detect_anomalies(features_df.copy())

    anomaly_outputs = {
        "GNN": gnn_out["anomaly_score"].values,
        "DeepSeek_MCHC": mchc_out["anomaly_score"].values,
        "Mamba_SSM": mamba_out["anomaly_score"].values,
        "xLSTM": xlstm_out["anomaly_score"].values,
    }

    for model_name, scores in anomaly_outputs.items():
        results.append(BenchmarkResult(model=model_name, task="anomaly", metric_name="mean_score", metric_value=float(np.mean(scores))))
        results.append(BenchmarkResult(model=model_name, task="anomaly", metric_name="max_score", metric_value=float(np.max(scores))))
        if anomaly_ground_truth is not None and len(anomaly_ground_truth) == len(scores):
            mse = mean_squared_error(anomaly_ground_truth, scores)
            results.append(BenchmarkResult(model=model_name, task="anomaly", metric_name="mse_vs_anomaly_corrected", metric_value=float(mse)))

    # ---------- Trajectory models ----------
    mamba_traj = MambaTrajectoryPredictor(input_size=features_df.shape[1], sequence_length=2)
    xlstm_traj = XLSTMTrajectoryPredictor(input_size=features_df.shape[1], sequence_length=2)

    # Build simple next-step target for comparison
    target = raw_df[["latitude", "longitude"]].shift(-1).dropna().values

    mamba_pred = mamba_traj.predict(features_df)
    xlstm_pred = xlstm_traj.predict(features_df)

    if len(mamba_pred) > 0:
        y = target[: len(mamba_pred)]
        pred = mamba_pred.numpy()
        results.append(BenchmarkResult("Mamba_Trajectory", "trajectory", "mae", float(mean_absolute_error(y, pred))))
        results.append(BenchmarkResult("Mamba_Trajectory", "trajectory", "rmse", float(np.sqrt(mean_squared_error(y, pred)))))

    if len(xlstm_pred) > 0:
        y = target[: len(xlstm_pred)]
        pred = xlstm_pred.numpy()
        results.append(BenchmarkResult("xLSTM_Trajectory", "trajectory", "mae", float(mean_absolute_error(y, pred))))
        results.append(BenchmarkResult("xLSTM_Trajectory", "trajectory", "rmse", float(np.sqrt(mean_squared_error(y, pred)))))

    out_df = pd.DataFrame([r.__dict__ for r in results])
    metrics_path = f"reports/metrics/model_benchmark_{date}.csv"
    out_df.to_csv(metrics_path, index=False)

    # ---------- Plot: key metrics ----------
    plot_df = out_df[out_df.metric_name.isin(["mse_vs_anomaly_corrected", "mae", "rmse", "mean_score"])].copy()
    if not plot_df.empty:
        plt.figure(figsize=(12, 6))
        for metric in plot_df.metric_name.unique():
            subset = plot_df[plot_df.metric_name == metric]
            plt.bar([f"{m}\n{metric}" for m in subset.model], subset.metric_value, alpha=0.8, label=metric)
        plt.xticks(rotation=30, ha="right")
        plt.ylabel("Metric Value")
        plt.title(f"Model Comparison Metrics ({date})")
        plt.tight_layout()
        plt_path = f"reports/plots/model_comparison_{date}.png"
        plt.savefig(plt_path, dpi=140)
        plt.close()
    else:
        plt_path = ""

    return metrics_path, plt_path


if __name__ == "__main__":
    d = datetime.now().strftime("%Y-%m-%d")
    try:
        metrics_file, plot_file = run_benchmark(d)
    except RuntimeError:
        # bootstrap sample data path when pipeline hasn't populated storage yet
        from src.processing.transformer import TelemetryTransformer
        from src.storage.storage_manager import StorageManager

        TelemetryTransformer().process_raw_files()
        StorageManager().move_processed_to_storage()
        metrics_file, plot_file = run_benchmark(d)

    print(f"Metrics written: {metrics_file}")
    if plot_file:
        print(f"Plot written: {plot_file}")
