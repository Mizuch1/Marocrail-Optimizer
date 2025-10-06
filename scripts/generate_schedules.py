"""
Generate synthetic train schedules for Moroccan railway network
"""
import json
import os
import random
from datetime import datetime, timedelta

# Peak hours: 6-9 AM and 5-8 PM (higher frequency)
PEAK_HOURS = [(6, 9), (17, 20)]
DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Busy routes get more trains
BUSY_ROUTES = [
    (1, 3), (2, 3), (3, 1), (3, 2),  # Casa-Rabat corridor
    (2, 8), (8, 2),  # Casa-Marrakech
    (3, 7), (7, 3)   # Rabat-Fès
]

def is_peak_hour(hour):
    """Check if hour is during peak time"""
    return any(start <= hour < end for start, end in PEAK_HOURS)

def generate_departure_times(route, is_busy):
    """Generate departure times for a route"""
    times = []
    
    if is_busy:
        # Busy routes: every 30min during peak, every 90min off-peak
        for hour in range(5, 23):
            if is_peak_hour(hour):
                times.extend([f"{hour:02d}:00", f"{hour:02d}:30"])
            else:
                if hour % 2 == 0:
                    times.append(f"{hour:02d}:00")
    else:
        # Normal routes: every 60min during peak, every 2-3h off-peak
        for hour in range(6, 22):
            if is_peak_hour(hour):
                times.append(f"{hour:02d}:00")
            else:
                if hour % 3 == 0:
                    times.append(f"{hour:02d}:00")
    
    return times

def assign_train_to_schedule(trains, route, departure_time):
    """Assign appropriate train type based on route and time"""
    hour = int(departure_time.split(':')[0])
    
    # Al Boraq only on major routes (Casa-Rabat, Casa-Tanger)
    if route['distance_km'] > 200 or (route['origin_station_id'] <= 3 and route['destination_station_id'] <= 3):
        if is_peak_hour(hour):
            # During peak, prioritize high capacity
            train_types = ['TNR', 'Al Boraq', 'Regular']
        else:
            train_types = ['Al Boraq', 'TNR', 'Regular']
    else:
        train_types = ['TNR', 'Regular']
    
    # Filter trains by type
    available_trains = [t for t in trains if t['train_type'] in train_types]
    return random.choice(available_trains)

def calculate_arrival_time(departure_time, duration_minutes):
    """Calculate arrival time from departure and duration"""
    dep_time = datetime.strptime(departure_time, "%H:%M")
    arr_time = dep_time + timedelta(minutes=duration_minutes)
    return arr_time.strftime("%H:%M")

def generate_schedules(stations, routes, trains):
    """Generate daily schedules"""
    schedules = []
    schedule_id = 1
    
    for route in routes:
        # Check if this is a busy route
        is_busy = (route['origin_station_id'], route['destination_station_id']) in BUSY_ROUTES
        
        # Generate departure times
        departure_times = generate_departure_times(route, is_busy)
        
        # Get origin station details
        origin_station = next(s for s in stations if s['station_id'] == route['origin_station_id'])
        
        for departure_time in departure_times:
            # Assign train
            train = assign_train_to_schedule(trains, route, departure_time)
            
            # Calculate arrival time
            arrival_time = calculate_arrival_time(departure_time, route['typical_duration_minutes'])
            
            # Assign platform (random within station capacity)
            platform = random.randint(1, origin_station['platform_count'])
            
            # Create schedule for each day of week
            for day in DAYS_OF_WEEK:
                # Weekend patterns: fewer trains on Sunday
                if day == 'Sunday' and random.random() < 0.3:
                    continue
                
                schedule = {
                    "schedule_id": schedule_id,
                    "train_id": train['train_id'],
                    "train_number": train['train_number'],
                    "route_id": route['route_id'],
                    "origin_station_id": route['origin_station_id'],
                    "origin_name": route['origin_name'],
                    "destination_station_id": route['destination_station_id'],
                    "destination_name": route['destination_name'],
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "platform": platform,
                    "day_of_week": day,
                    "status": "scheduled",
                    "train_type": train['train_type'],
                    "capacity": train['capacity']
                }
                
                schedules.append(schedule)
                schedule_id += 1
    
    return schedules

def save_schedules(schedules):
    """Save schedules to JSON file"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'schedules.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(schedules, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Generated {len(schedules)} weekly schedules")
    print(f"  - Average per day: {len(schedules)//7}")
    print(f"[OK] Saved to: {output_file}")
    return schedules

if __name__ == "__main__":
    # Load data
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    with open(os.path.join(data_dir, 'stations.json'), 'r', encoding='utf-8') as f:
        stations = json.load(f)
    
    with open(os.path.join(data_dir, 'routes.json'), 'r', encoding='utf-8') as f:
        routes = json.load(f)
    
    with open(os.path.join(data_dir, 'trains.json'), 'r', encoding='utf-8') as f:
        trains = json.load(f)
    
    schedules = generate_schedules(stations, routes, trains)
    save_schedules(schedules)
