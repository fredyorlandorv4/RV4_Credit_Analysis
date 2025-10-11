#!/usr/bin/env python3
"""
Test script to verify that predictions are now generating different results
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_pipeline import model
from sample_data import generate_and_save_data
import pandas as pd

def test_predictions():
    print("Testing prediction variability...")
    
    # Generate new sample data
    print("1. Generating new sample data...")
    sample_path = 'data/test_credit_data.csv'
    generate_and_save_data(sample_path, num_records=100)
    
    # Train model with new data
    print("2. Training model with new data...")
    df = pd.read_csv(sample_path)
    result = model.train(df, source='test')
    print(f"Training result: {result}")
    
    # Test same input multiple times to verify variation
    print("3. Testing prediction variability...")
    
    test_input = {
        'Age': 35,
        'Gender': 'Male',
        'Credit_Score': 680,
        'Monthly_Income': 45000,
        'DTI_Ratio': 0.32,
        'Employment_Status': 'Employed',
        'Documents_Submitted': 4,
        'Employment_Duration_Months': 24,
        'Processing_Time_Days': 15,
        'completeness_score': 80,
        'Days_In_Process': 15,
        'Communication_Frequency': 1.5,
        'Loan_Amount': 500000,
        'Property_Price': 750000,
        'Down_Payment': 250000,
        'Interest_Rate': 7.5,
        'Loan_Duration': 20
    }
    
    print("\nTesting same input 5 times:")
    for i in range(5):
        prediction = model.predict(test_input)
        print(f"Test {i+1}: Approval: {prediction['success_probability']}%, Withdrawal Risk: {prediction['withdrawal_risk']}%")
    
    # Test different inputs
    print("\nTesting different credit scores:")
    
    test_cases = [
        {'Credit_Score': 500, 'DTI_Ratio': 0.45, 'desc': 'Poor credit, high DTI'},
        {'Credit_Score': 650, 'DTI_Ratio': 0.35, 'desc': 'Average credit, normal DTI'},
        {'Credit_Score': 750, 'DTI_Ratio': 0.25, 'desc': 'Excellent credit, low DTI'},
        {'Credit_Score': 720, 'DTI_Ratio': 0.50, 'desc': 'Good credit, high DTI'}
    ]
    
    for case in test_cases:
        test_input_case = test_input.copy()
        test_input_case.update(case)
        prediction = model.predict(test_input_case)
        print(f"{case['desc']}: Approval: {prediction['success_probability']}%, Withdrawal Risk: {prediction['withdrawal_risk']}%")
    
    # Clean up
    try:
        os.remove(sample_path)
    except:
        pass
    
    print("\nTest completed!")

if __name__ == '__main__':
    test_predictions()