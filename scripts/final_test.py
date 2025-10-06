"""
Final comprehensive system test
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_system():
    print("="*60)
    print("  MarocRail-Optimizer - Final System Test")
    print("="*60)
    
    errors = []
    
    # Test 1: Database
    print("\n[1/5] Testing database...")
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'marocrail.db')
        if not os.path.exists(db_path):
            errors.append("Database file not found")
        else:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM stations")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"[OK] Database accessible - {count} stations")
    except Exception as e:
        errors.append(f"Database error: {e}")
        print(f"[FAIL] {e}")
    
    # Test 2: ML Models
    print("\n[2/5] Testing ML models...")
    try:
        import joblib
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        clf = joblib.load(os.path.join(model_dir, 'delay_classifier.pkl'))
        reg = joblib.load(os.path.join(model_dir, 'delay_regressor.pkl'))
        print(f"[OK] ML models loaded")
    except Exception as e:
        errors.append(f"ML model error: {e}")
        print(f"[FAIL] {e}")
    
    # Test 3: Flask app
    print("\n[3/5] Testing Flask app...")
    try:
        from app import app
        client = app.test_client()
        response = client.get('/dashboard')
        if response.status_code == 200:
            print(f"[OK] Flask app working")
        else:
            errors.append(f"Flask returned status {response.status_code}")
    except Exception as e:
        errors.append(f"Flask error: {e}")
        print(f"[FAIL] {e}")
    
    # Test 4: API endpoints
    print("\n[4/5] Testing API endpoints...")
    try:
        from app import app
        client = app.test_client()
        
        endpoints = [
            '/api/stations',
            '/api/routes',
            '/api/schedules',
            '/api/analytics/overview'
        ]
        
        all_ok = True
        for endpoint in endpoints:
            response = client.get(endpoint)
            if response.status_code != 200:
                all_ok = False
                errors.append(f"{endpoint} failed")
        
        if all_ok:
            print(f"[OK] All API endpoints working")
    except Exception as e:
        errors.append(f"API error: {e}")
        print(f"[FAIL] {e}")
    
    # Test 5: Data files
    print("\n[5/5] Testing data files...")
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        required_files = [
            'stations.json', 'routes.json', 'trains.json',
            'schedules.json', 'delays.json', 'passengers.json'
        ]
        
        missing = []
        for filename in required_files:
            if not os.path.exists(os.path.join(data_dir, filename)):
                missing.append(filename)
        
        if missing:
            errors.append(f"Missing data files: {', '.join(missing)}")
            print(f"[FAIL] Missing: {', '.join(missing)}")
        else:
            print(f"[OK] All data files present")
    except Exception as e:
        errors.append(f"Data files error: {e}")
        print(f"[FAIL] {e}")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print(f"  [FAILED] {len(errors)} errors found:")
        for err in errors:
            print(f"    - {err}")
    else:
        print("  [SUCCESS] All tests passed!")
        print("="*60)
        print("\n  System is ready for deployment!")
        print("  Run: python app.py")
        print("  Open: http://localhost:5000")
    print("="*60)
    print()
    
    return len(errors) == 0

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)
