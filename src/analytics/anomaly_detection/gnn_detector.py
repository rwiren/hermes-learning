import torch
import pandas as pd
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv # Example GNN layer
import torch.nn.functional as F
import torch_geometric
from datetime import datetime

from src.features.anomaly_prep import AnomalyPreprocessor

class SimpleGNN(torch.nn.Module):
    """
    A simple Graph Neural Network module for demonstration.
    This can be replaced with more complex GNN architectures (e.g., heterogeneous GNNs).
    """
    def __init__(self, num_node_features, hidden_channels, num_classes):
        super().__init__()
        self.conv1 = GCNConv(num_node_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, num_classes)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv2(x, edge_index)
        return x

class GNNDetector:
    """
    Detects anomalies in ADS-B telemetry data using Graph Neural Networks.
    Models the sensor grid and aircraft trajectories as a geometric graph.
    """
    def __init__(self, sensor_locations: dict, num_features: int, hidden_channels: int = 16, num_classes: int = 2):
        self.sensor_locations = sensor_locations # {sensor_id: (lat, lon)}
        self.model = SimpleGNN(num_features, hidden_channels, num_classes)
        # Optimizer and loss function for training (if applicable)
        # self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
        # self.criterion = torch.nn.CrossEntropyLoss() # or anomaly specific loss

    def _build_graph(self, telemetry_df: pd.DataFrame) -> Data:
        """
        Builds a PyTorch Geometric Data object from telemetry data.
        Nodes represent aircraft observations. Edges can be temporal or spatial.
        This is a simplified approach; a more robust GNN would use heterogeneous graphs.
        """
        if telemetry_df.empty:
            raise ValueError("Telemetry DataFrame is empty. Cannot build graph.")

        # Node features (aircraft telemetry)
        # Using features extracted by AnomalyPreprocessor as node features
        x = torch.tensor(telemetry_df[['latitude', 'longitude', 'altitude', 'velocity', 'track', 'ground_speed', 'vertical_rate']].values, dtype=torch.float)

        # Edge construction: For simplicity, let's create a fully connected graph for now
        # In a real scenario, this would be based on proximity, temporal adjacency, or sensor visibility
        num_nodes = telemetry_df.shape[0]
        row = torch.arange(num_nodes).repeat_interleave(num_nodes)
        col = torch.arange(num_nodes).repeat(num_nodes)
        edge_index = torch.stack([row, col], dim=0)

        # Add self-loops to the edge_index
        edge_index = torch_geometric.utils.add_self_loops(edge_index)[0]

        data = Data(x=x, edge_index=edge_index)
        return data

    def detect_anomalies(self, telemetry_df: pd.DataFrame) -> pd.DataFrame:
        """
        Orchestrates graph building, model inference, and anomaly scoring.
        Returns the telemetry DataFrame with an added 'anomaly_score' column.
        """
        if telemetry_df.empty:
            print("No telemetry data to process for anomaly detection.")
            return telemetry_df

        try:
            data = self._build_graph(telemetry_df)
        except ValueError as e:
            print(f"Error building graph: {e}")
            telemetry_df['anomaly_score'] = 0.0 # Assign default score
            return telemetry_df

        # Placeholder for actual anomaly detection logic using the GNN model
        self.model.eval()
        with torch.no_grad():
            # The output of the GNN can be interpreted as anomaly scores or used for a downstream anomaly detection head
            # For this prototype, let's assume the GNN directly outputs a score or a feature representation
            # from which we can derive an anomaly score (e.g., reconstruction error from an autoencoder GNN)
            # Here, we'll just use a dummy score for now.
            
            # For a classification task, output would be logits:
            # logits = self.model(data.x, data.edge_index)
            # anomaly_scores = torch.softmax(logits, dim=1)[:, 1] # Assuming class 1 is anomaly

            # For a simple embedding-based anomaly detection:
            # embeddings = self.model(data.x, data.edge_index) # Assuming GNN outputs embeddings
            # anomaly_scores = torch.rand(data.num_nodes) # Dummy scores
            
            anomaly_scores = torch.rand(data.num_nodes) # Dummy random scores for illustration

        telemetry_df['anomaly_score'] = anomaly_scores.numpy()
        return telemetry_df

if __name__ == '__main__':
    # Example usage with AnomalyPreprocessor
    # Define dummy sensor locations
    sensor_locations = {
        'north': (60.192059, 24.945831),
        'west': (60.200000, 24.800000),
        'east': (60.100000, 25.100000),
    }

    preprocessor = AnomalyPreprocessor()
    today_date = datetime.now().strftime('%Y-%m-%d')
    prepared_data = preprocessor.prepare_data(today_date)

    if not prepared_data.empty:
        # Determine number of features from the prepared data
        num_features = prepared_data.shape[1]
        gnn_detector = GNNDetector(sensor_locations, num_features=num_features)
        anomalies = gnn_detector.detect_anomalies(prepared_data)

        print(f"Detected anomalies head:\n{anomalies.head()}")
        print(f"Anomalies shape: {anomalies.shape}")
    else:
        print("No data prepared for GNN anomaly detection.")
