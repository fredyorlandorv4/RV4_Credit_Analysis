# RV4 Credit Recommendation Dashboard - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Machine Learning Pipeline](#machine-learning-pipeline)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Frontend Components](#frontend-components)
6. [Configuration Guide](#configuration-guide)
7. [Deployment Instructions](#deployment-instructions)
8. [Troubleshooting](#troubleshooting)

## Architecture Overview

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (HTML/JS/CSS) │◄──►│   (Flask/Python)│◄──►│   (MySQL)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   ML Pipeline   │
                       │   (LightGBM)    │
                       └─────────────────┘
```

### Technology Stack
- **Backend Framework**: Flask 2.3+
- **Database**: MySQL 8.0+ with SQLAlchemy ORM
- **Machine Learning**: LightGBM, scikit-learn
- **Frontend**: Bootstrap 5, Plotly.js, vanilla JavaScript
- **Authentication**: Flask-Login with bcrypt password hashing
- **Data Processing**: Pandas, NumPy

### Directory Structure
```
rv4-credit-dashboard/
├── app_updated.py              # Main Flask application
├── auth.py                     # Authentication blueprint
├── database.py                 # Database models and ORM
├── model_pipeline.py           # ML pipeline and models
├── plotting.py                 # Chart generation functions
├── sample_data.py              # Data generation utilities
├── translations.py             # Multi-language support
├── requirements.txt            # Python dependencies
├── data/                       # Training data storage
│   ├── README.md
│   └── training_data_*.csv
├── weights/                    # Trained model storage
│   ├── *.pkl                   # Model files
│   ├── model_metadata.json
│   └── training_history.json
├── templates/                  # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── auth/
│   └── *.html
├── static/                     # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── application_data/           # Saved application data
├── report/                     # Generated reports
└── notebook/                   # Jupyter notebooks
    └── experiments.ipynb
```

## Machine Learning Pipeline

### Model Architecture

#### 1. Approval Prediction Model
- **Algorithm**: LightGBM Gradient Boosting
- **Type**: Binary Classification
- **Target**: Approval probability (0-1)
- **Features**: 25+ engineered features
- **Performance**: 85-95% accuracy typical

#### 2. Withdrawal Risk Model
- **Algorithm**: LightGBM Gradient Boosting
- **Type**: Binary Classification
- **Target**: Withdrawal risk probability (0-1)
- **Features**: Same feature set as approval model
- **Performance**: 70-85% accuracy typical

### Feature Engineering

#### Financial Features
```python
# Loan-to-Value Ratio
LTV_Ratio = Loan_Amount / Property_Price

# Down Payment Percentage
Down_Payment_Percentage = Down_Payment / Property_Price

# Monthly Payment Calculation
Monthly_Payment = Loan_Amount * (r * (1+r)^n) / ((1+r)^n - 1)
where r = monthly_interest_rate, n = number_of_payments

# Debt-to-Income Ratio
DTI_Ratio = Monthly_Payment / Monthly_Income
```

#### Risk Indicators
```python
# Processing Time Risk
Long_Processing = 1 if Days_In_Process > 30 else 0

# Documentation Risk
Low_Documentation = 1 if Documents_Submitted < 3 else 0

# Credit Score Categories
Credit_Risk_Category = pd.cut(Credit_Score, 
    bins=[0, 580, 620, 680, 740, 850],
    labels=['Very_Poor', 'Poor', 'Fair', 'Good', 'Excellent'])
```

### Model Training Process

#### Data Preprocessing
1. **Feature Engineering**: Create financial ratios and risk indicators
2. **Data Validation**: Check for required columns and data quality
3. **Feature Selection**: Exclude non-predictive columns
4. **Data Splitting**: Stratified train/test split (80/20)
5. **Preprocessing Pipeline**: StandardScaler for numeric, OneHotEncoder for categorical

#### Training Configuration
```python
LGBMClassifier(
    objective='binary',
    class_weight='balanced',      # Handle imbalanced data
    n_estimators=100,            # Number of boosting rounds
    learning_rate=0.05,          # Conservative learning rate
    max_depth=6,                 # Prevent overfitting
    min_child_samples=20,        # Minimum samples per leaf
    random_state=42,             # Reproducibility
    verbosity=-1                 # Suppress warnings
)
```

#### Model Evaluation Metrics
- **Accuracy**: Overall prediction accuracy
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under the receiver operating characteristic curve

## Database Schema

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    role ENUM('admin', 'employee') NOT NULL,
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);
```

#### Applications Table
```sql
CREATE TABLE applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id VARCHAR(50) UNIQUE NOT NULL,
    agent_id INT NOT NULL,
    client_name VARCHAR(200) NOT NULL,
    dpi VARCHAR(50),
    email VARCHAR(120),
    phone VARCHAR(20),
    address TEXT,
    application_type VARCHAR(50),
    age INT,
    gender VARCHAR(20),
    marital_status VARCHAR(50),
    monthly_income DECIMAL(15,2),
    credit_score INT,
    dti_ratio DECIMAL(5,4),
    employment_status VARCHAR(50),
    employment_duration_months INT,
    loan_amount DECIMAL(15,2),
    property_price DECIMAL(15,2),
    down_payment DECIMAL(15,2),
    interest_rate DECIMAL(5,3),
    loan_duration INT,
    product_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'In-Process',
    documents_submitted INT DEFAULT 0,
    processing_time_days INT DEFAULT 0,
    communication_frequency DECIMAL(5,2) DEFAULT 1.0,
    completeness_score DECIMAL(5,2) DEFAULT 0,
    approval_probability DECIMAL(5,4),
    withdrawal_risk DECIMAL(5,4),
    loan_decision VARCHAR(50),
    notes TEXT,
    application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_contact_date DATETIME,
    FOREIGN KEY (agent_id) REFERENCES users(id)
);
```

#### Activity Logs Table
```sql
CREATE TABLE activity_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NULL,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    description TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### Documents Table
```sql
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    document_name VARCHAR(200) NOT NULL,
    is_received BOOLEAN DEFAULT FALSE,
    received_date DATETIME,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id)
);
```

### Relationships
- Users (1) → Applications (N)
- Applications (1) → Documents (N)
- Applications (1) → Activity Logs (N)
- Users (1) → Activity Logs (N)

## API Endpoints

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/profile` - User profile management

### Application Management
- `GET /dashboard` - Main dashboard view
- `GET /my_clients` - User's applications list
- `GET /client/<int:app_id>` - Application details
- `POST /new_application` - Create new application
- `POST /update_application/<int:app_id>` - Update application
- `POST /update_documents/<int:app_id>` - Update document status

### Machine Learning Endpoints
- `POST /api/train/database` - Train models from database
- `POST /api/train/csv` - Train models from CSV upload
- `POST /api/train/sample` - Train models with generated data
- `GET /api/model/info` - Get model information
- `POST /predictions` - Run ML predictions
- `POST /recommendations` - Generate recommendations

### Utility Endpoints
- `GET /api/applications/recent` - Recent applications
- `GET /api/applications/stats` - Application statistics
- `GET /completeness` - Document completeness check
- `GET /withdrawal` - Withdrawal risk assessment

## Frontend Components

### Dashboard Structure
```
Dashboard
├── Header (Navigation, User Menu)
├── Model Status Bar (Admin Only)
├── User Stats Bar
├── KPI Cards (4 metrics)
├── Recent Applications Table
├── Interactive Charts
│   ├── Trends Chart (Time series)
│   ├── Funnel Chart (Application flow)
│   ├── Correlation Heatmap
│   ├── Box Plot (Credit scores)
│   └── Sunburst Chart (Demographics)
├── Quick Actions Panel
└── Train Model Modal (Admin Only)
```

### JavaScript Libraries
- **Plotly.js**: Interactive charts and visualizations
- **Bootstrap 5**: UI components and responsive design
- **Fetch API**: AJAX requests to backend
- **Custom JS**: Application-specific functionality

### Chart Configurations
All charts use a consistent dark theme configuration:
```javascript
const darkLayout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#F3F4F6', family: 'Inter, sans-serif' },
    xaxis: { gridcolor: 'rgba(55, 65, 81, 0.3)' },
    yaxis: { gridcolor: 'rgba(55, 65, 81, 0.3)' }
};
```

## Configuration Guide

### Environment Variables
```bash
# Application Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
FLASK_ENV=production

# Database Configuration
DATABASE_URL=mysql+pymysql://user:password@host:port/database
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Session Configuration
REMEMBER_COOKIE_DURATION=7  # days
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

### Database Configuration
```python
# app_updated.py
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 
    'mysql+pymysql://user:password@localhost/rv4_credit')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
```

### Model Configuration
```python
# model_pipeline.py
MODEL_CONFIG = {
    'n_estimators': 100,
    'learning_rate': 0.05,
    'max_depth': 6,
    'min_child_samples': 20,
    'class_weight': 'balanced',
    'random_state': 42
}
```

## Deployment Instructions

### Production Deployment with Gunicorn

#### 1. Install Production Dependencies
```bash
pip install gunicorn
pip install mysql-connector-python
```

#### 2. Create Gunicorn Configuration
```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 3. Run with Gunicorn
```bash
gunicorn -c gunicorn.conf.py app_updated:app
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /path/to/rv4-credit-dashboard/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app_updated:app"]
```

### Database Migration
```bash
# Create database backup
mysqldump -u username -p database_name > backup.sql

# Apply schema changes
mysql -u username -p database_name < migration.sql

# Verify migration
python -c "from app_updated import app, db; app.app_context().db.create_all()"
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```python
# Check connection
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://user:pass@host/db')
try:
    connection = engine.connect()
    print("✅ Database connection successful")
    connection.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

#### 2. Model Training Failures
```python
# Debug model training
from model_pipeline import model
import pandas as pd

# Check data quality
df = pd.read_csv('data/training_data.csv')
print(f"Data shape: {df.shape}")
print(f"Status distribution: {df['Status'].value_counts()}")
print(f"Missing values: {df.isnull().sum().sum()}")

# Test training
result = model.train(df, source='debug')
print(f"Training result: {result}")
```

#### 3. Permission Issues
```bash
# Fix file permissions
chmod -R 755 /path/to/rv4-credit-dashboard
chown -R www-data:www-data /path/to/rv4-credit-dashboard

# Fix directory permissions
mkdir -p data weights application_data report
chmod 755 data weights application_data report
```

### Logging Configuration
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Application logger
app.logger.setLevel(logging.INFO)
```

### Performance Monitoring
```python
# Add timing middleware
@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    app.logger.info(f"Request to {request.endpoint} took {duration:.3f}s")
    return response
```

### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    """System health check endpoint"""
    try:
        # Check database
        db.session.execute('SELECT 1')
        
        # Check models
        model_status = model.get_model_info()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'models': 'loaded' if model_status['models_loaded'] else 'not_loaded',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

## Performance Optimization

### Database Optimization
- Index frequently queried columns
- Use connection pooling
- Implement query optimization
- Regular database maintenance

### Model Optimization
- Feature selection and dimensionality reduction
- Model hyperparameter tuning
- Batch prediction for multiple applications
- Model caching for frequent predictions

### Frontend Optimization
- Minimize HTTP requests
- Compress static assets
- Implement client-side caching
- Optimize chart rendering

---

**Last Updated**: September 2025  
**Version**: 2.0.0  
**Maintainer**: RV4 Development Team
