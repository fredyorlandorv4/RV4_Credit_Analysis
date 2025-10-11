
# 🏦 RV4 Credit Analysis Dashboard

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Private-red.svg)](LICENSE)
[![ML](https://img.shields.io/badge/ML-LightGBM-orange.svg)](https://lightgbm.readthedocs.io/)

A smart, bilingual credit analysis web dashboard built with Flask and machine learning. It provides predictive insights, real-time KPIs, strategic recommendations, and document completeness evaluations for credit applications.

## 🌟 Key Features

### 📊 Analytics Dashboard
- Real-time KPIs: approval rates, rejection trends, average processing time
- Visualizations: trends, funnel, heatmap, box plot, and sunburst charts via Plotly
- Dynamic data updates with CSV uploads

### 🤖 Machine Learning Predictions
- **Approval Probability** using LightGBM
- **Withdrawal Risk Assessment** using hybrid rule-based logic
- **Document Completeness Scoring** with critical/supplementary weights

### 📂 Document Completeness System
- Weighted scoring engine: 60% critical docs, 40% supplementary
- Visual feedback: progress bar, badges, and status messages
- Multilingual labels and alerts

### 🧠 Strategic Recommendation Engine
- Actionable recommendations for underwriting, risk mitigation, and document requests
- Loan-to-value and payment-to-income metrics evaluated
- Priority-based risk flags and suggestions

### 🌍 Bilingual Support
- Full interface in **English** and **Spanish**
- Session-persistent language switching
- Localized terminology and cultural adaptation

### ✨ Additional Highlights
- Intelligent data input form with automatic model retraining
- Real-time CSV backups and updates
- Responsive dark-mode interface with Bootstrap 5

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+
pip install -r requirements.txt
```

### Run the App

```bash
python app.py
```

Then visit: `http://localhost:5000`

## 🏗️ Directory Structure

```
rv4-credit-dashboard/
├── data/                    # CSV files (sample + user uploaded)
├── templates/               # Jinja2 HTML templates
├── static/                  # CSS/JS assets
├── app.py                   # Flask main app
├── model_pipeline.py        # ML training & prediction logic
├── plotting.py              # Plotly chart generation
├── sample_data.py           # Synthetic data generator
├── translations.py          # Multilingual support
├── requirements.txt         # Python dependencies
```

## 🧠 ML Pipeline Overview

### Model: LightGBM Classifier

#### Training Flow
```python
train_models(data_path='data/credit_data.csv')
```

#### Input Features
- Credit Score, Income, DTI Ratio
- Age, Employment Status
- Loan Amount, Duration, Rate, Property Price

#### Outputs
- `success_probability` (0–100%)
- `withdrawal_risk` (0–100%)
- `completeness_score` (0–100%)

#### Prediction Example
```python
predict_outcomes(applicant_dict)
```

## 📊 Interactive Visualizations (Plotly)
- 📈 Trends: Application volumes by time & status
- 📉 Funnel: Submission → Review → Decision
- 🔥 Heatmap: Feature correlation
- 📦 Box Plot: Credit score vs. status
- 🌞 Sunburst: Breakdown by gender & status

## 📄 API Endpoints (via HTML Forms)

| Route             | Description                         |
|------------------|-------------------------------------|
| `/predictions`   | Predict approval/withdrawal         |
| `/completeness`  | Evaluate document integrity         |
| `/withdrawal`    | Manual risk scoring (rule-based)    |
| `/recommendations` | Generate next-step suggestions   |
| `/retrain`       | Upload CSV and retrain models       |
| `/use_sample_data` | Reset to default sample data      |
| `/data_input`    | Add new applicant + retrain models  |

## 🌐 Internationalization

| Language | Status |
|----------|--------|
| 🇺🇸 English | ✅ Full support |
| 🇪🇸 Spanish | ✅ Full support |

- Culturally adapted content
- Currency (GTQ) formatting
- Language toggle via session

## 📈 Performance (on sample data)

- ✅ Model Accuracy: ~92.5%
- 🔁 Retraining: Automatic on new uploads
- 📊 Metrics: AUC, Precision, Recall, Approval %

## 🛡️ Security & Reliability

- Session-based language persistence
- Input validation for form entries
- Secure storage of uploaded data (no external DB)
- CSV backups and fail-safe retraining

## 📝 Contributing

1. Fork the repository
2. Create a branch (`feature/your-feature`)
3. Commit your changes
4. Open a Pull Request

## 📄 License

This project is under **Private License**. Unauthorized use or distribution is prohibited. Contact the developer for access.

## 📞 Support

For help, email [support@rv4analytics.com](mailto:support@rv4analytics.com)

---

**Built with ❤️ for fair, data-driven lending decisions.**
