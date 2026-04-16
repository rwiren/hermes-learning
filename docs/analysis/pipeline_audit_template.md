# Pipeline Audit Template

## Audit Metadata
- **Date of Audit:** [YYYY-MM-DD]
- **Auditor:** [Name/Agent]
- **Pipeline Version:** [Semantic Version]
- **Data Scope:** [e.g., ADS-B Telemetry 2026-04-16]
- **Collection Source URL:** [http://www.securingskies.eu:8080/]
- **Collection Window:** [start UTC -> end UTC]
- **Collection Cadence:** [e.g., every 30s]

## 1. Executive Summary
[Brief overview of pipeline health and findings]

## 2. Operational Metrics
### 2.1 Data Volume
- **Raw Records Processed:** [Count]
- **Storage Growth (MB):** [Size]
- **Transformation Efficiency:** [Time/Records ratio]

### 2.2 Data Integrity
- **Validation Failures:** [Count of rejected records]
- **Anomaly Detection Rate:** [Percentage of flagged records]

### 2.3 Strict Evaluation Metrics
- **Dataset Prevalence:** [positives / total]
- **AUROC (per model):** [table]
- **AUPRC (per model):** [table]
- **F1 / Precision / Recall @0.5:** [table]
- **MCC and Balanced Accuracy:** [table]
- **Confusion Matrix:** [TN, FP, FN, TP per model]

## 3. Detailed Findings
[Deep dive into specific anomalies, spoof signals, UAV detections, or bottlenecks]

## 4. Conclusion & Recommendations
[Action items to improve pipeline robustness, model calibration, and data quality]
## 3. Detailed Findings
[Deep dive into specific anomalies or bottleneck observations]

## 4. Conclusion & Recommendations
[Action items to improve pipeline robustness or data quality]
