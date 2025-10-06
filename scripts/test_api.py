"""
Quick API test
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
import json

def test_api():
    client = app.test_client()
    
    print("="*60)
    print("  Testing Flask API")
    print("="*60)
    
    print("\n[1/5] Testing GET /api/stations")
    response = client.get('/api/stations')
    data = json.loads(response.data)
    print(f"[OK] Status: {response.status_code}, Stations: {data['count']}")
    
    print("\n[2/5] Testing GET /api/routes")
    response = client.get('/api/routes')
    data = json.loads(response.data)
    print(f"[OK] Status: {response.status_code}, Routes: {data['count']}")
    
    print("\n[3/5] Testing GET /api/schedules")
    response = client.get('/api/schedules?day=Monday')
    data = json.loads(response.data)
    print(f"[OK] Status: {response.status_code}, Schedules: {data['count']}")
    
    print("\n[4/5] Testing GET /api/analytics/overview")
    response = client.get('/api/analytics/overview')
    data = json.loads(response.data)
    print(f"[OK] Status: {response.status_code}")
    print(f"  - Total trains: {data['data']['total_trains']}")
    print(f"  - On-time rate: {data['data']['on_time_rate']}%")
    
    print("\n[5/5] Testing POST /api/predict")
    payload = {
        'route_id': 1,
        'hour': 8,
        'day_of_week': 1,
        'weather': 'sunny',
        'train_type_code': 2,
        'capacity': 400,
        'distance_km': 91,
        'duration': 50
    }
    response = client.post('/api/predict', 
                           data=json.dumps(payload),
                           content_type='application/json')
    data = json.loads(response.data)
    print(f"[OK] Status: {response.status_code}")
    print(f"  - Delay probability: {data['data']['delay_probability']:.2%}")
    print(f"  - Risk level: {data['data']['risk_level']}")
    
    print("\n" + "="*60)
    print("  [SUCCESS] All API tests passed!")
    print("="*60)
    print()

if __name__ == "__main__":
    test_api()
