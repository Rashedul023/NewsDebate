import requests
import json
from datetime import datetime

print("="*60)
print("📱 TESTING NEWSDEBATE API")
print("="*60)

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, url):
    """Test an API endpoint and print result"""
    print(f"\n🔍 Testing {name}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Success! Status: {response.status_code}")
            data = response.json()
            if 'results' in data:
                print(f"Found {len(data['results'])} articles")
            elif isinstance(data, list):
                print(f"Found {len(data)} items")
            return True
        else:
            print(f"Failed! Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Test all endpoints
test_endpoint("Home page", f"{BASE_URL}/")
test_endpoint("API Root", f"{BASE_URL}/api/")
test_endpoint("Articles List", f"{BASE_URL}/api/articles/")
test_endpoint("Statistics", f"{BASE_URL}/api/articles/stats/")
test_endpoint("Sources List", f"{BASE_URL}/api/articles/sources/")

# Test first article if exists
try:
    response = requests.get(f"{BASE_URL}/api/articles/")
    data = response.json()
    if data['results'] and len(data['results']) > 0:
        first_id = data['results'][0]['id']
        test_endpoint(f"Article Detail (ID: {first_id})", f"{BASE_URL}/api/articles/{first_id}/")
except:
    pass


print("✅ API TESTING COMPLETE")
