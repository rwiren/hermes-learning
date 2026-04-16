"""
pipeline_visualizer.py

This module provides visualization capabilities for the ADS-B data pipeline.
It generates analytical plots to monitor the health, volume, and efficiency
of the transformation and storage processes.

Common Visualizations:
1. Data Volume over Time: Tracks the number of records or file sizes processed.
2. Transformation Efficiency: Monitor processing time vs data volume.
3. Storage Growth: Monitors the expansion of the data lake.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class PipelineVisualizer:
    """
    Generates analytical plots for monitoring the ADS-B pipeline.
    """
    def __init__(self, 
                 data_storage_path='data/storage', 
                 reports_plots_path='reports/plots',
                 metrics_csv_path='reports/metrics/pipeline_stats.csv'):
        self.storage_path = data_storage_path
        self.plots_path = reports_plots_path
        self.metrics_path = metrics_csv_path
        
        os.makedirs(self.plots_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.metrics_path), exist_ok=True)
        
        sns.set_theme(style="darkgrid")

    def _get_storage_stats(self):
        """
        Aggregates file counts and sizes from the storage directory.
        """
        stats = []
        # Walk through the date-partitioned storage
        for root, dirs, files in os.walk(self.storage_path):
            for file in files:
                if file.endswith('.parquet'):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    # Extract date from path (assuming structure is .../YYYY-MM-DD/...)
                    parts = root.split(os.sep)
                    # Look for the date pattern in the path
                    date_str = None
                    for part in reversed(parts):
                        try:
                            # Simple check for YYYY-MM-DD format
                            datetime.strptime(part, '%Y-%m-%d')
                            date_str = part
                            break
                        except ValueError:
                            continue
                    
                    if date_str:
                        stats.append({
                            'date': datetime.strptime(date_str, '%Y-%m-%d'),
                            'size_mb': file_size / (1024 * 1024),
                            'file': file
                        })
        
        return pd.DataFrame(stats)

    def generate_storage_growth_plot(self):
        """
        Plot: Cumulative storage growth over time.
        """
        df = self._get_storage_points()
        if df.empty:
            print("No storage data found for growth plot.")
            return

        df = df.sort_values('date')
        df['cumulative_size'] = df['size_mb'].cumsum()

        plt.figure(figsize=(10, 6))
        plt.plot(df['date'], df['cumulative_size'], marker='o', linestyle='-', color='b')
        plt.title('Cumulative Data Storage Growth (MB)')
        plt.xlabel('Date')
        plt.ylabel('Total Size (MB)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plot_file = os.path.join(self.plots_path, f'storage_growth_{datetime.now().strftime("%Y%m%d")}.png')
        plt.savefig(plot_file)
        plt.close()
        print(f"Generated storage growth plot: {plot_file}")

    def _get_storage_points(self):
        # Helper to wrap the internal stats logic
        return self._get_storage_stats()

    def generate_daily_volume_plot(self):
        """
        Plot: Number of records/files processed per day.
        """
        df = self._get_storage_stats()
        if df.empty:
            print("No storage data found for volume plot.")
            return

        df_daily = df.groupby('date').size().reset_index(name='file_count')

        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_daily, x='date', y='file_count', palette='viridis')
        plt.title('Daily Processed File Count')
        plt.xlabel('Date')
        plt.ylabel('Number of Parquet Files')
        plt.xticks(rotation=45)
        plt.tight_layout()

        plot_file = os.path.join(self.plots_path, f'daily_volume_{datetime.now().strftime("%Y%m%d")}.png')
        plt.savefig(plot_file)
        plt.close()
        print(f"Generated daily volume plot: {plot_file}")

    def run_all_visualizations(self):
        """
        Executes all available visual analytic tasks.
        """
        print("Starting pipeline visualization suite...")
        self.generate_storage_growth_plot()
        self.generate_daily_volume_plot()
        print("Visualization suite complete.")

if __name__ == "__main__":
    # For standalone testing
    visualizer = PipelineVisualizer()
    visualizer.run_all_visualizations()
