# Training Buttons Debug Guide

## Fixes Applied

### 1. JavaScript Syntax Error Fixed
- Fixed the broken JavaScript at the end of dashboard.html template
- Added proper error handling in training functions
- Added console logging for debugging

### 2. Improved Error Handling in Python Endpoints
- Enhanced `/api/train/database` endpoint with better session management
- Improved `/api/train/csv` endpoint with file validation and cleanup
- Enhanced `/api/train/sample` endpoint with sample data generation validation
- Added comprehensive error messages and logging

### 3. Enhanced Model Training Pipeline
- Reduced minimum records requirement for testing (from 50 to 10)
- Added better error handling for small datasets
- Improved stratified splitting with fallback to random split
- Added verbose logging for debugging

### 4. Frontend Improvements
- Added debug JavaScript file for testing
- Improved button styling and interactions
- Enhanced progress tracking and error reporting
- Better modal styling and responsiveness

## Debugging Steps

### 1. Check if Flask App is Running
The app should be running on http://127.0.0.1:5000
Look for these messages in terminal:
```
✅ Database initialized successfully!
* Running on http://127.0.0.1:5000
```

### 2. Test Training Endpoints in Browser
1. Open browser and navigate to http://127.0.0.1:5000
2. Login as admin user
3. Open browser developer tools (F12)
4. In console, run: `debugTraining()`
5. Check console for responses

### 3. Manual Training Test
1. Click "Train Model" button on dashboard
2. Try "Sample Data" option first (should work)
3. Check browser console for any JavaScript errors
4. Check terminal for Python errors

### 4. Common Issues and Solutions

#### Issue: "Admin access required"
- Make sure you're logged in as an admin user
- Check user role in database

#### Issue: "Insufficient data"
- The database needs at least 10 applications for training
- Use "Sample Data" option to generate test data first

#### Issue: JavaScript errors
- Check browser console (F12 -> Console tab)
- Look for missing functions or syntax errors

#### Issue: Modal not opening
- Check if Bootstrap JS is loaded
- Verify modal HTML is present
- Check for CSS conflicts

### 5. Testing Sample Data Generation
Run in terminal:
```bash
python -c "from sample_data import generate_and_save_data; generate_and_save_data('data/test.csv', 50)"
```

### 6. Testing Model Training Directly
Run in terminal:
```python
from model_pipeline import model
import pandas as pd

# Test with sample data
from sample_data import generate_and_save_data
generate_and_save_data('data/test.csv', 100)
df = pd.read_csv('data/test.csv')
result = model.train(df, 'test')
print(result)
```

## Expected Behavior

### Sample Data Training
1. Click "Use Sample" button
2. Should see progress: "Loading data..." -> "Training models..." -> "Complete!"
3. Results should show model metrics
4. Page should refresh showing updated model info

### Database Training
1. Click "Start Training" under Database option
2. If sufficient data exists, should train successfully
3. If insufficient data, should show error message

### CSV Upload Training
1. Click "Select File" and choose a CSV
2. File should be validated and processed
3. Training should proceed if CSV format is correct

## Files Modified
- app_updated.py (API endpoints)
- model_pipeline.py (training logic)
- templates/dashboard.html (frontend)
- static/js/debug_training.js (debugging)

## Next Steps if Issues Persist
1. Check Flask app logs in terminal
2. Check browser console for JavaScript errors
3. Verify all dependencies are installed
4. Test with minimal dataset first
5. Check file permissions for weights directory
