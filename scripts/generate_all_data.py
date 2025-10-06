"""
Master script to generate all synthetic data
Run this to create the complete dataset
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generate_stations import generate_stations
from scripts.generate_routes import generate_routes, save_routes
from scripts.generate_trains import generate_trains, save_trains
from scripts.generate_schedules import generate_schedules, save_schedules
from scripts.generate_delays import generate_delays_for_period, save_delays
from scripts.generate_passengers import generate_passengers_for_period, save_passengers
from datetime import datetime, timedelta
import json

def load_json(filename):
    """Load JSON data file"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Generate all synthetic data"""
    print("=" * 60)
    print("  MarocRail-Optimizer - Data Generation")
    print("=" * 60)
    print()
    
    # Step 1: Generate stations
    print("[1/6] Generating stations...")
    stations = generate_stations()
    print()
    
    # Step 2: Generate routes
    print("[2/6] Generating routes...")
    routes = generate_routes(stations)
    save_routes(routes)
    print()
    
    # Step 3: Generate trains
    print("[3/6] Generating trains...")
    trains = generate_trains()
    save_trains(trains)
    print()
    
    # Step 4: Generate schedules
    print("[4/6] Generating schedules...")
    schedules = generate_schedules(stations, routes, trains)
    save_schedules(schedules)
    print()
    
    # Step 5: Generate delays (6 months history)
    print("[5/6] Generating delay history...")
    start_date = datetime.now() - timedelta(days=180)
    delays = generate_delays_for_period(schedules, start_date, days=180)
    save_delays(delays)
    print()
    
    # Step 6: Generate passenger flow
    print("[6/6] Generating passenger flow data...")
    passengers = generate_passengers_for_period(schedules, start_date, days=180)
    save_passengers(passengers)
    print()
    
    # Summary
    print("=" * 60)
    print("  [SUCCESS] Data Generation Complete!")
    print("=" * 60)
    print(f"  Stations: {len(stations)}")
    print(f"  Routes: {len(routes)}")
    print(f"  Trains: {len(trains)}")
    print(f"  Weekly Schedules: {len(schedules)}")
    print(f"  Delay Records (6 months): {len(delays)}")
    print(f"  Passenger Records (6 months): {len(passengers)}")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Create database: python scripts/create_database.py")
    print("  2. Train ML model: python scripts/train_model.py")
    print()

if __name__ == "__main__":
    main()
