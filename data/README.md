# Training Data Directory

This directory contains training data files automatically saved during model training sessions.

## File Naming Convention

Files are automatically named with the following pattern:
```
training_data_{source}_{timestamp}.csv
```

Where:
- `{source}` indicates the data source: `database`, `csv`, or `sample`
- `{timestamp}` is in format: `YYYYMMDD_HHMMSS`

## Examples

- `training_data_database_20250911_143052.csv` - Database training session
- `training_data_csv_20250911_151230.csv` - CSV upload training session
- `training_data_sample_20250911_162145.csv` - Generated data training session

## Data Content

Each file contains the complete dataset used for that specific training session, including:
- All application records with features
- Target variables (Status)
- Engineered features (DTI ratios, LTV ratios, etc.)
- Calculated risk indicators

## Usage

These files can be used for:
- Model reproducibility and validation
- Data quality analysis
- Audit trail documentation
- Research and experimentation

## Retention Policy

- Files are kept indefinitely for audit purposes
- Consider archiving files older than 2 years
- Always maintain at least the last 10 training sessions
