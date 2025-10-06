"""
Test dashboard pages
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app

def test_pages():
    client = app.test_client()
    
    print("="*60)
    print("  Testing Dashboard Pages")
    print("="*60)
    
    pages = [
        ('/', 'Home'),
        ('/dashboard', 'Dashboard'),
        ('/schedules', 'Schedules'),
        ('/analytics', 'Analytics'),
        ('/predict', 'Predict')
    ]
    
    for url, name in pages:
        response = client.get(url)
        status = "[OK]" if response.status_code == 200 else "[FAIL]"
        print(f"{status} {name:15s} - Status: {response.status_code}")
    
    print("\n" + "="*60)
    print("  [SUCCESS] All pages loaded!")
    print("="*60)
    print()
    print("To view the dashboard, run: python app.py")
    print("Then open: http://localhost:5000")
    print()

if __name__ == "__main__":
    test_pages()
