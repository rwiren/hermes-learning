import pandas as pd
import os

class AnomalyPreprocessor:
    """
    Prepares telemetry data from data/storage for anomaly detection.
    Extracts relevant features and structures the data for ML models.
    """
    def __init__(self, storage_path='data/storage'):
        self.storage_path = storage_path

    def load_telemetry_data(self, date: str) -> pd.DataFrame:
        """
        Loads telemetry data for a specific date from the data lake.
        Args:
            date (str): The date in 'YYYY-MM-DD' format.
        Returns:
            pd.DataFrame: A DataFrame containing the telemetry data for the given date.
        """
        file_path = os.path.join(self.storage_path, date, f'sample_telemetry_{date}.parquet')
        if not os.path.exists(file_path):
            print(f"Error: Data file not found for date {date} at {file_path}")
            return pd.DataFrame()
        return pd.read_parquet(file_path)

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts and prepares features from the raw telemetry DataFrame for anomaly detection.
        This is a placeholder for more sophisticated feature engineering.
        Args:
            df (pd.DataFrame): The raw telemetry DataFrame.
        Returns:
            pd.DataFrame: DataFrame with extracted features.
        """
        # Placeholder for feature extraction
        # For now, we'll use a subset of direct telemetry as features
        features = df[['latitude', 'longitude', 'altitude', 'velocity', 'track', 'ground_speed', 'vertical_rate']]
        return features

    def prepare_data(self, date: str) -> pd.DataFrame:
        """
        Orchestrates the data loading and feature extraction for anomaly detection.
        Args:
            date (str): The date in 'YYYY-MM-DD' format.
        Returns:
            pd.DataFrame: Prepared features for anomaly detection.
        """
        df = self.load_telemetry_data(date)
        if df.empty:
            return pd.DataFrame()
        return self.extract_features(df)

if __name__ == '__main__':
    # Example usage
    preprocessor = AnomalyPreprocessor()
    today_date = datetime.now().strftime('%Y-%m-%d')
    prepared_data = preprocessor.prepare_data(today_date)

    if not prepared_data.empty:
        print(f"Prepared data head:\n{prepared_data.head()}")
        print(f"Prepared data shape: {prepared_data.shape}")
    else:
        print("No data prepared.")
