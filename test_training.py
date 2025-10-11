#!/usr/bin/env python3
"""
Test script to verify training endpoints work correctly
Run this with the Flask app running to test the training buttons
"""

import requests
import json
import sys
import time

# Flask app URL
BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(endpoint, name, data=None, files=None):
    """Test a specific training endpoint"""
    print(f"\n{'='*50}")
    print(f"Testing {name}")
    print(f"{'='*50}")
    
    try:
        if files:
            response = requests.post(f"{BASE_URL}{endpoint}", files=files)
        elif data:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}")
        
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result.get('success', False)
        except:
            print(f"Raw Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_sample_data_generation():
    """Test sample data generation"""
    print(f"\n{'='*50}")
    print("Testing Sample Data Generation")
    print(f"{'='*50}")
    
    try:
        from sample_data import generate_and_save_data
        import os
        
        # Remove existing file if it exists
        sample_path = 'data/credit_data.csv'
        if os.path.exists(sample_path):
            os.remove(sample_path)
            print("Removed existing sample data file")
        
        # Generate new sample data
        generate_and_save_data(sample_path, num_records=100)
        
        if os.path.exists(sample_path):
            print("✅ Sample data generated successfully")
            
            # Check file size
            import pandas as pd
            df = pd.read_csv(sample_path)
            print(f"Generated {len(df)} records")
            print(f"Status distribution: {df['Status'].value_counts().to_dict()}")
            return True
        else:
            print("❌ Sample data file not found after generation")
            return False
            
    except Exception as e:
        print(f"❌ Error generating sample data: {str(e)}")
        return False

def main():
    print("Testing Credit Recommendation App Training Endpoints")
    print("Make sure the Flask app is running on http://127.0.0.1:5000")
    
    # Test if server is running
    try:
        response = requests.get(BASE_URL)
        print(f"✅ Server is running (Status: {response.status_code})")
    except:
        print("❌ Server is not running. Please start the Flask app first.")
        sys.exit(1)
    
    # Test sample data generation first
    sample_success = test_sample_data_generation()
    
    # Test training endpoints (these will fail without login, but we can see the response)
    print("\n" + "="*60)
    print("Testing Training Endpoints (expect authentication errors)")
    print("="*60)
    
    results = {}
    
    # Test sample training
    results['sample'] = test_endpoint('/api/train/sample', 'Sample Data Training')
    
    # Test database training
    results['database'] = test_endpoint('/api/train/database', 'Database Training')
    
    # Test model info
    results['info'] = test_endpoint('/api/model/info', 'Model Info', data={})
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Sample Data Generation: {'✅' if sample_success else '❌'}")
    
    for test_name, success in results.items():
        status = '✅' if success else '❌'
        print(f"{test_name.title()} Endpoint: {status}")
    
    print(f"\nNote: Authentication errors are expected when testing without login.")
    print(f"The important thing is that endpoints respond correctly to requests.")

if __name__ == '__main__':
    main()
