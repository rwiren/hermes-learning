import pandas as pd
from datetime import datetime

from src.features.anomaly_prep import AnomalyPreprocessor
from src.analytics.anomaly_detection.gnn_detector import GNNDetector
from src.analytics.anomaly_detection.mchc_detector import MCHCDectector
from src.analytics.anomaly_detection.mamba_detector import MambaDetector
from src.analytics.anomaly_detection.xlstm_detector import XLSTMDetector

def run_initial_anomaly_evaluation(date: str, anomaly_threshold: float = 0.5):
    """
    Runs an initial evaluation of the anomaly detection models.
    Args:
        date (str): The date in 'YYYY-MM-DD' format for which to evaluate data.
        anomaly_threshold (float): The threshold above which a score is considered an anomaly.
    """
    print(f"\n--- Running Initial Anomaly Evaluation for {date} ---")

    preprocessor = AnomalyPreprocessor()
    prepared_data = preprocessor.prepare_data(date)

    if prepared_data.empty:
        print("No data prepared for evaluation. Skipping anomaly detection.")
        return

    num_features = prepared_data.shape[1]
    num_records = prepared_data.shape[0]

    # --- GNN Detector Evaluation ---
    print("\nEvaluating GNN Detector...")
    sensor_locations = {'north': (60.192059, 24.945831), 'west': (60.200000, 24.800000), 'east': (60.100000, 25.100000)}
    gnn_detector = GNNDetector(sensor_locations, num_features=num_features)
    gnn_anomalies = gnn_detector.detect_anomalies(prepared_data.copy())
    gnn_anomaly_count = (gnn_anomalies['anomaly_score'] > anomaly_threshold).sum()
    print(f"GNN Detector: Detected {gnn_anomaly_count}/{num_records} anomalies (>{anomaly_threshold}).")

    # --- MCHC Detector Evaluation ---
    print("\nEvaluating MCHC Detector...")
    mchc_detector = MCHCDectector(num_node_features=num_features)
    mchc_anomalies = mchc_detector.detect_anomalies(prepared_data.copy())
    mchc_anomaly_count = (mchc_anomalies['anomaly_score'] > anomaly_threshold).sum()
    print(f"MCHC Detector: Detected {mchc_anomaly_count}/{num_records} anomalies (>{anomaly_threshold}).")

    # --- Mamba Detector Evaluation ---
    # Mamba requires a minimum sequence length, check if data is sufficient
    print("\nEvaluating Mamba Detector...")
    if num_records >= 10: # Assuming sequence_length=10 as in mamba_detector.py example
        mamba_detector = MambaDetector(d_model=num_features, sequence_length=10)
        mamba_anomalies = mamba_detector.detect_anomalies(prepared_data.copy())
        mamba_anomaly_count = (mamba_anomalies['anomaly_score'] > anomaly_threshold).sum()
        print(f"Mamba Detector: Detected {mamba_anomaly_count}/{num_records} anomalies (>{anomaly_threshold}).")
    else:
        print(f"Mamba Detector: Not enough records ({num_records}) for sequence length 10. Skipping.")

    # --- xLSTM Detector Evaluation ---
    # xLSTM requires a minimum sequence length, check if data is sufficient
    print("\nEvaluating xLSTM Detector...")
    if num_records >= 10: # Assuming sequence_length=10 as in xlstm_detector.py example
        xlstm_detector = XLSTMDetector(input_size=num_features, sequence_length=10)
        xlstm_anomalies = xlstm_detector.detect_anomalies(prepared_data.copy())
        xlstm_anomaly_count = (xlstm_anomalies['anomaly_score'] > anomaly_threshold).sum()
        print(f"xLSTM Detector: Detected {xlstm_anomaly_count}/{num_records} anomalies (>{anomaly_threshold}).")
    else:
        print(f"xLSTM Detector: Not enough records ({num_records}) for sequence length 10. Skipping.")

    print("\n--- Initial Anomaly Evaluation Complete ---")

if __name__ == '__main__':
    today_date = datetime.now().strftime('%Y-%m-%d')
    run_initial_anomaly_evaluation(today_date)
