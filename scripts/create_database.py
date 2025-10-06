"""
Create SQLite database and load all synthetic data
"""
import sqlite3
import json
import os
from datetime import datetime

def get_db_path():
    """Get database file path"""
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'marocrail.db')

def get_data_path(filename):
    """Get data file path"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    return os.path.join(data_dir, filename)

def load_json(filename):
    """Load JSON data file"""
    with open(get_data_path(filename), 'r', encoding='utf-8') as f:
        return json.load(f)

def create_database():
    """Create database with schema"""
    db_path = get_db_path()
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"[INFO] Removed existing database")
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(db_path), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Execute schema (split by semicolon to handle multiple statements)
    for statement in schema_sql.split(';'):
        if statement.strip():
            cursor.execute(statement)
    
    conn.commit()
    print(f"[OK] Database created: {db_path}")
    
    return conn, cursor

def load_stations(cursor):
    """Load stations data"""
    stations = load_json('stations.json')
    
    for station in stations:
        cursor.execute("""
            INSERT INTO stations (station_id, name, city, latitude, longitude, 
                                 platform_count, capacity, is_major)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            station['station_id'],
            station['name'],
            station['city'],
            station['latitude'],
            station['longitude'],
            station['platform_count'],
            station['capacity'],
            station['is_major']
        ))
    
    print(f"[OK] Loaded {len(stations)} stations")

def load_routes(cursor):
    """Load routes data"""
    routes = load_json('routes.json')
    
    for route in routes:
        cursor.execute("""
            INSERT INTO routes (route_id, origin_station_id, destination_station_id,
                               distance_km, typical_duration_minutes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            route['route_id'],
            route['origin_station_id'],
            route['destination_station_id'],
            route['distance_km'],
            route['typical_duration_minutes']
        ))
    
    print(f"[OK] Loaded {len(routes)} routes")

def load_trains(cursor):
    """Load trains data"""
    trains = load_json('trains.json')
    
    for train in trains:
        cursor.execute("""
            INSERT INTO trains (train_id, train_number, train_type, speed_kmh,
                               capacity, pricing_tier, operational_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            train['train_id'],
            train['train_number'],
            train['train_type'],
            train['speed_kmh'],
            train['capacity'],
            train['pricing_tier'],
            train['operational_status']
        ))
    
    print(f"[OK] Loaded {len(trains)} trains")

def load_schedules(cursor):
    """Load schedules data"""
    schedules = load_json('schedules.json')
    
    for schedule in schedules:
        cursor.execute("""
            INSERT INTO schedules (schedule_id, train_id, route_id, departure_time,
                                  arrival_time, platform, day_of_week, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            schedule['schedule_id'],
            schedule['train_id'],
            schedule['route_id'],
            schedule['departure_time'],
            schedule['arrival_time'],
            schedule['platform'],
            schedule['day_of_week'],
            schedule['status']
        ))
    
    print(f"[OK] Loaded {len(schedules)} schedules")

def load_delays(cursor):
    """Load delays data"""
    delays = load_json('delays.json')
    
    for delay in delays:
        cursor.execute("""
            INSERT INTO delays (delay_id, schedule_id, delay_minutes, delay_reason,
                               weather_condition, timestamp, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            delay['delay_id'],
            delay['schedule_id'],
            delay['delay_minutes'],
            delay['delay_reason'],
            delay['weather_condition'],
            delay['timestamp'],
            delay['resolved']
        ))
    
    print(f"[OK] Loaded {len(delays)} delay records")

def load_passengers(cursor):
    """Load passenger data"""
    passengers = load_json('passengers.json')
    
    # Batch insert for performance
    batch_size = 1000
    for i in range(0, len(passengers), batch_size):
        batch = passengers[i:i+batch_size]
        cursor.executemany("""
            INSERT INTO passengers (record_id, schedule_id, passenger_count,
                                   booking_date, travel_date)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (p['record_id'], p['schedule_id'], p['passenger_count'],
             p['booking_date'], p['travel_date'])
            for p in batch
        ])
        if (i + batch_size) % 10000 == 0:
            print(f"  Progress: {min(i + batch_size, len(passengers))}/{len(passengers)} records...")
    
    print(f"[OK] Loaded {len(passengers)} passenger records")

def verify_database(cursor):
    """Verify database integrity"""
    print("\n[INFO] Verifying database...")
    
    tables = ['stations', 'routes', 'trains', 'schedules', 'delays', 'passengers']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} records")
    
    # Check foreign key constraints
    cursor.execute("PRAGMA foreign_key_check")
    fk_violations = cursor.fetchall()
    
    if fk_violations:
        print(f"\n[WARNING] Foreign key violations found: {len(fk_violations)}")
        for violation in fk_violations[:5]:
            print(f"  {violation}")
    else:
        print("\n[OK] No foreign key violations")

def main():
    """Main database creation process"""
    print("=" * 60)
    print("  MarocRail-Optimizer - Database Creation")
    print("=" * 60)
    print()
    
    # Create database
    conn, cursor = create_database()
    
    try:
        # Load all data
        print("\n[1/6] Loading stations...")
        load_stations(cursor)
        
        print("\n[2/6] Loading routes...")
        load_routes(cursor)
        
        print("\n[3/6] Loading trains...")
        load_trains(cursor)
        
        print("\n[4/6] Loading schedules...")
        load_schedules(cursor)
        
        print("\n[5/6] Loading delays...")
        load_delays(cursor)
        
        print("\n[6/6] Loading passenger data...")
        load_passengers(cursor)
        
        # Commit all changes
        conn.commit()
        
        # Verify
        verify_database(cursor)
        
        # Optimize database
        print("\n[INFO] Optimizing database...")
        cursor.execute("ANALYZE")
        cursor.execute("VACUUM")
        conn.commit()
        
        print("\n" + "=" * 60)
        print("  [SUCCESS] Database created and populated!")
        print("=" * 60)
        print(f"\n  Database: {get_db_path()}")
        print(f"  Size: {os.path.getsize(get_db_path()) / 1024 / 1024:.2f} MB")
        print()
        
    except Exception as e:
        print(f"\n[ERROR] Database creation failed: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
