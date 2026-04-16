import torch
import torch.nn as nn
import pandas as pd


class MambaTrajectoryModel(nn.Module):
    """
    Placeholder trajectory predictor using an identity block to emulate unavailable
    mamba_ssm in local environment while preserving interface contract.
    """

    def __init__(self, input_size: int, hidden_size: int = 64, output_size: int = 2):
        super().__init__()
        self.backbone = nn.Identity()
        self.head = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [batch, seq_len, features]
        pooled = self.backbone(x).mean(dim=1)
        return self.head(pooled)


class MambaTrajectoryPredictor:
    def __init__(self, input_size: int = 7, sequence_length: int = 10):
        self.sequence_length = sequence_length
        self.model = MambaTrajectoryModel(input_size=input_size)

    def _make_sequences(self, df: pd.DataFrame):
        feature_cols = [
            "latitude",
            "longitude",
            "altitude",
            "velocity",
            "track",
            "ground_speed",
            "vertical_rate",
        ]
        if len(df) <= self.sequence_length:
            return None, None

        x_seq = []
        y_seq = []
        values = df[feature_cols].values
        targets = df[["latitude", "longitude"]].values

        for i in range(len(df) - self.sequence_length):
            x_seq.append(values[i : i + self.sequence_length])
            y_seq.append(targets[i + self.sequence_length])

        return torch.tensor(x_seq, dtype=torch.float32), torch.tensor(y_seq, dtype=torch.float32)

    def predict(self, df: pd.DataFrame) -> torch.Tensor:
        x, _ = self._make_sequences(df)
        if x is None:
            return torch.empty((0, 2))
        self.model.eval()
        with torch.no_grad():
            return self.model(x)
