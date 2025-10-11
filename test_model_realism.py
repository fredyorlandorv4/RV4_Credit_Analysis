#!/usr/bin/env python3
"""Test script to verify model accuracy improvements"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_pipeline import ModelPipeline
import pandas as pd
import numpy as np

def create_realistic_test_data(n_samples=100):
    """Create realistic credit application data"""
    np.random.seed(42)
    
    # Generate correlated features
    credit_scores = np.random.normal(680, 80, n_samples)
    credit_scores = np.clip(credit_scores, 300, 850)
    
    # DTI is somewhat correlated with approval outcome
    dti_ratios = np.random.normal(0.35, 0.1, n_samples)
    dti_ratios = np.clip(dti_ratios, 0.1, 0.8)
    
    # Income somewhat correlated with credit score
    incomes = 25000 + (credit_scores - 300) * 100 + np.random.normal(0, 10000, n_samples)
    incomes = np.clip(incomes, 20000, 120000)
    
    # Create realistic approval outcomes
    # Higher credit score and lower DTI = higher approval chance
    approval_probs = []
    for i in range(n_samples):
        cs = credit_scores[i]
        dti = dti_ratios[i]
        
        # Base probability
        prob = 0.4
        
        # Credit score effect
        if cs >= 750:
            prob += 0.3
        elif cs >= 700:
            prob += 0.2
        elif cs >= 650:
            prob += 0.1
        elif cs < 600:
            prob -= 0.2
        
        # DTI effect
        if dti <= 0.3:
            prob += 0.15
        elif dti <= 0.4:
            prob += 0.05
        elif dti > 0.5:
            prob -= 0.2
        
        # Add noise
        prob += np.random.normal(0, 0.1)
        prob = max(0.05, min(0.85, prob))  # Realistic bounds
        approval_probs.append(prob)
    
    # Generate status based on probabilities
    statuses = []
    for prob in approval_probs:
        rand = np.random.random()
        if rand < prob:
            statuses.append('Approved')
        elif rand < prob + 0.1:  # 10% withdrawal rate
            statuses.append('Withdrawn')
        elif rand < prob + 0.15:  # 5% in process
            statuses.append('In-Process')
        else:
            statuses.append('Declined')
    
    data = pd.DataFrame({
        'Age': np.random.randint(25, 65, n_samples),
        'Gender': np.random.choice(['Male', 'Female'], n_samples),
        'Credit_Score': credit_scores,
        'Monthly_Income': incomes,
        'DTI_Ratio': dti_ratios,
        'Employment_Status': np.random.choice(['Employed', 'Self-Employed'], n_samples, p=[0.8, 0.2]),
        'Employment_Duration_Months': np.random.randint(6, 120, n_samples),
        'Loan_Amount': np.random.randint(200000, 1000000, n_samples),
        'Property_Price': np.random.randint(300000, 1500000, n_samples),
        'Down_Payment': np.random.randint(50000, 400000, n_samples),
        'Interest_Rate': np.random.uniform(5.0, 9.0, n_samples),
        'Loan_Duration': np.random.choice([15, 20, 25, 30], n_samples),
        'Documents_Submitted': np.random.randint(2, 6, n_samples),
        'Processing_Time_Days': np.random.randint(5, 60, n_samples),
        'Days_In_Process': np.random.randint(5, 60, n_samples),
        'Communication_Frequency': np.random.uniform(0.5, 2.0, n_samples),
        'completeness_score': np.random.uniform(40, 100, n_samples),
        'Status': statuses
    })
    
    return data

def test_model_realism():
    """Test if model produces realistic accuracy"""
    print("Creating realistic test data...")
    test_data = create_realistic_test_data(200)
    
    print(f"Status distribution:")
    print(test_data['Status'].value_counts())
    print(f"Approval rate: {(test_data['Status'] == 'Approved').mean():.1%}")
    
    print("\nInitializing model...")
    model = ModelPipeline()
    
    print("Training model...")
    result = model.train(test_data, source='realism_test')
    
    if result['success']:
        print(f"\n✅ Training successful!")
        print(f"Records used: {result['records_used']}")
        
        metrics = result['metrics']
        print(f"\nModel Performance:")
        print(f"Approval model accuracy: {metrics['approval']['accuracy']:.3f}")
        print(f"Withdrawal model accuracy: {metrics['withdrawal']['accuracy']:.3f}")
        
        if 'cv_mean_accuracy' in metrics['approval']:
            print(f"Approval CV accuracy: {metrics['approval']['cv_mean_accuracy']:.3f} ± {metrics['approval']['cv_std_accuracy']:.3f}")
        if 'cv_mean_accuracy' in metrics['withdrawal']:
            print(f"Withdrawal CV accuracy: {metrics['withdrawal']['cv_mean_accuracy']:.3f} ± {metrics['withdrawal']['cv_std_accuracy']:.3f}")
        
        # Test predictions
        print(f"\n🧪 Testing predictions...")
        
        # Test cases
        test_cases = [
            {
                'name': 'Excellent candidate',
                'Credit_Score': 780,
                'DTI_Ratio': 0.25,
                'Monthly_Income': 70000,
                'Employment_Duration_Months': 48,
                'completeness_score': 95
            },
            {
                'name': 'Average candidate',
                'Credit_Score': 680,
                'DTI_Ratio': 0.35,
                'Monthly_Income': 45000,
                'Employment_Duration_Months': 24,
                'completeness_score': 80
            },
            {
                'name': 'Poor candidate',
                'Credit_Score': 580,
                'DTI_Ratio': 0.55,
                'Monthly_Income': 28000,
                'Employment_Duration_Months': 8,
                'completeness_score': 40
            }
        ]
        
        for case in test_cases:
            try:
                prediction = model.predict(case)
                print(f"\n{case['name']}:")
                print(f"  Approval probability: {prediction['success_probability']:.1f}%")
                print(f"  Withdrawal risk: {prediction['withdrawal_risk']:.1f}%")
            except Exception as e:
                print(f"Error predicting {case['name']}: {e}")
        
        # Check if accuracies are realistic (not too high)
        approval_acc = metrics['approval']['accuracy']
        withdrawal_acc = metrics['withdrawal']['accuracy']
        
        if approval_acc > 0.85:
            print(f"\n⚠️  Warning: Approval accuracy ({approval_acc:.3f}) seems unrealistically high")
        else:
            print(f"\n✅ Approval accuracy ({approval_acc:.3f}) is within realistic range")
            
        if withdrawal_acc > 0.85:
            print(f"⚠️  Warning: Withdrawal accuracy ({withdrawal_acc:.3f}) seems unrealistically high")
        else:
            print(f"✅ Withdrawal accuracy ({withdrawal_acc:.3f}) is within realistic range")
            
    else:
        print(f"❌ Training failed: {result['message']}")

if __name__ == "__main__":
    test_model_realism()