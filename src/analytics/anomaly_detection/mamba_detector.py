import torch
import torch.nn as nn
import pandas as pd
from src.features.anomaly_prep import AnomalyPreprocessor
from datetime import datetime

class MambaAnomalyModel(nn.Module):
    """
    A simple wrapper around the Mamba SSM for anomaly detection.
    This can be expanded to include sequence processing and an anomaly head.
    """
    def __init__(self, d_model: int, n_layer: int, vocab_size: int = 1):
        super().__init__()
        # Placeholder implementation (mamba_ssm unavailable on this environment)
        self.mamba = nn.Identity()
        self.anomaly_head = nn.Linear(d_model, 1)

    def forward(self, x):
        # x is expected to be of shape (batch_size, sequence_length, d_model)
        mamba_output = self.mamba(x) # (batch_size, sequence_length, d_model)
        # For anomaly detection, we might take the last hidden state or pool outputs
        # For simplicity, taking the mean over the sequence dimension
        pooled_output = mamba_output.mean(dim=1)
        anomaly_score_logits = self.anomaly_head(pooled_output)
        return torch.sigmoid(anomaly_score_logits) # Output a score between 0 and 1

class MambaDetector:
    """
    Detects slow \"drift\" attacks in ADS-B telemetry using Mamba State Space Models.
    Designed for efficient long-context trajectory tracking.
    """
    def __init__(self, d_model: int = 7, n_layer: int = 2, sequence_length: int = 10):
        # d_model should match the number of features from AnomalyPreprocessor
        self.d_model = d_model
        self.sequence_length = sequence_length
        self.model = MambaAnomalyModel(d_model, n_layer)

    def _prepare_sequences(self, telemetry_df: pd.DataFrame) -> torch.Tensor:
        """
        Prepares telemetry data into sequences suitable for Mamba.
        Assumes telemetry_df contains numerical features.
        """
        if telemetry_df.empty:
            raise ValueError("Telemetry DataFrame is empty. Cannot prepare sequences.")

        # Convert DataFrame to a tensor of sequences
        # This is a simplified approach, real implementation would handle padding, batching, etc.
        # For demonstration, we'll create overlapping sequences
        sequences = []
        for i in range(len(telemetry_df) - self.sequence_length + 1):
            sequence = telemetry_df.iloc[i:i+self.sequence_length].values
            sequences.append(sequence)
        
        if not sequences:
            raise ValueError(f"Not enough data to create sequences of length {self.sequence_length}.")

        return torch.tensor(sequences, dtype=torch.float)

    def detect_anomalies(self, telemetry_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detects anomalies in telemetry data using the Mamba model.
        Returns the telemetry DataFrame with an added 'anomaly_score' column.
        """
        if telemetry_df.empty:
            print("No telemetry data to process for Mamba anomaly detection.")
            telemetry_df['anomaly_score'] = 0.0
            return telemetry_df

        try:
            sequences = self._prepare_sequences(telemetry_df)
        except ValueError as e:
            print(f"Error preparing sequences: {e}")
            telemetry_df['anomaly_score'] = 0.0
            return telemetry_df

        self.model.eval()
        with torch.no_grad():
            # MambaAnomalyModel outputs a single anomaly score per sequence
            # We need to map these back to individual telemetry records.
            # For simplicity, assign the sequence anomaly score to the last element of the sequence.
            # A more robust approach would involve averaging scores over overlapping sequences.
            anomaly_scores_tensor = self.model(sequences).squeeze(-1).numpy()
            
            # Initialize anomaly scores for the entire DataFrame
            telemetry_df['anomaly_score'] = 0.0

            # Assign scores back to the DataFrame (simplified: assign to the last element of each sequence)
            # This will result in 0.0 for the first (sequence_length-1) records
            for i, score in enumerate(anomaly_scores_tensor):
                if i + self.sequence_length -1 < len(telemetry_df):
                    telemetry_df.loc[i + self.sequence_length - 1, 'anomaly_score'] = score

        return telemetry_df

if __name__ == '__main__':
    # Example usage with AnomalyPreprocessor
    preprocessor = AnomalyPreprocessor()
    today_date = datetime.now().strftime('%Y-%m-%d')
    prepared_data = preprocessor.prepare_data(today_date)

    if not prepared_data.empty and prepared_data.shape[0] >= 10: # Ensure enough data for sequence_length=10
        num_features = prepared_data.shape[1]
        mamba_detector = MambaDetector(d_model=num_features, sequence_length=10)
        anomalies = mamba_detector.detect_anomalies(prepared_data)

        print(f"Detected Mamba anomalies head:\n{anomalies.head(15)}")
        print(f"Anomalies shape: {anomalies.shape}")
    else:
        print("Not enough data prepared for Mamba anomaly detection or data is empty.")
