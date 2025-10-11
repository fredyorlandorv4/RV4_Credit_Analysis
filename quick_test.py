import requests
import json

def test_training_endpoints():
    """Test the training endpoints to see if they respond correctly"""
    base_url = "http://127.0.0.1:5000"
    
    print("Testing Training Endpoints")
    print("=" * 50)
    
    # Test endpoints (these will return 403 without login, but that's expected)
    endpoints = [
        ("/api/train/sample", "Sample Training"),
        ("/api/train/database", "Database Training"),
        ("/api/model/info", "Model Info")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.post(f"{base_url}{endpoint}")
            print(f"\n{name}:")
            print(f"  Status: {response.status_code}")
            try:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)}")
            except:
                print(f"  Response: {response.text}")
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("Note: 403 errors are expected without login")
    print("The important thing is that endpoints respond")

if __name__ == "__main__":
    test_training_endpoints()
