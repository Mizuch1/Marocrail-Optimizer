"""
Generate synthetic passenger flow data
"""
import json
import os
import random
from datetime import datetime, timedelta

# Busy routes have higher passenger counts
BUSY_ROUTES = {
    (1, 3): 1.5,  # Casa-Port to Rabat
    (2, 3): 1.5,  # Casa-Voyageurs to Rabat
    (3, 1): 1.5,  # Rabat to Casa-Port
    (3, 2): 1.5,  # Rabat to Casa-Voyageurs
    (2, 8): 1.3,  # Casa to Marrakech
    (8, 2): 1.3,  # Marrakech to Casa
}

def get_route_key(schedule):
    """Get route key for passenger multiplier"""
    return (schedule['origin_station_id'], schedule['destination_station_id'])

def is_peak_hour(hour):
    """Check if hour is during peak time"""
    return (6 <= hour <= 9) or (17 <= hour <= 20)

def calculate_passenger_count(schedule, day_name, is_holiday=False):
    """Calculate realistic passenger count"""
    base_capacity = schedule['capacity']
    hour = int(schedule['departure_time'].split(':')[0])
    
    # Base occupancy: 50-70% on average
    occupancy_rate = random.uniform(0.5, 0.7)
    
    # Peak hours: 80-95% occupancy
    if is_peak_hour(hour):
        occupancy_rate = random.uniform(0.8, 0.95)
    
    # Weekend patterns
    if day_name in ['Friday', 'Saturday']:
        occupancy_rate *= 1.2  # More weekend travel
    elif day_name == 'Sunday':
        occupancy_rate *= 0.8  # Less Sunday travel
    
    # Holiday boost
    if is_holiday:
        occupancy_rate *= 1.3
    
    # Busy route multiplier
    route_key = get_route_key(schedule)
    route_multiplier = BUSY_ROUTES.get(route_key, 1.0)
    occupancy_rate *= route_multiplier
    
    # Premium trains (Al Boraq) tend to have lower occupancy
    if schedule['train_type'] == 'Al Boraq':
        occupancy_rate *= 0.85
    
    # Cap at 100% and add some randomness
    occupancy_rate = min(occupancy_rate, 1.0)
    passenger_count = int(base_capacity * occupancy_rate)
    
    # Add randomness (±10%)
    variation = int(passenger_count * random.uniform(-0.1, 0.1))
    passenger_count = max(0, passenger_count + variation)
    
    return passenger_count

def generate_passengers_for_period(schedules, start_date, days=180):
    """Generate 6 months of passenger flow data"""
    passengers = []
    record_id = 1
    
    # Moroccan holidays (approximate)
    holidays = [
        datetime(2024, 1, 1),   # New Year
        datetime(2024, 5, 1),   # Labor Day
        datetime(2024, 7, 30),  # Throne Day
        datetime(2024, 8, 14),  # Oued Dahab
        # Add more as needed
    ]
    holiday_dates = {h.date() for h in holidays}
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        day_name = current_date.strftime("%A")
        is_holiday = current_date.date() in holiday_dates
        
        # Get schedules for this day
        day_schedules = [s for s in schedules if s['day_of_week'] == day_name]
        
        for schedule in day_schedules:
            # Booking date: typically 1-30 days before travel
            days_advance = random.choices(
                [1, 2, 3, 7, 14, 21, 30],
                weights=[0.15, 0.15, 0.15, 0.20, 0.15, 0.10, 0.10]
            )[0]
            booking_date = current_date - timedelta(days=days_advance)
            
            # Calculate passengers
            passenger_count = calculate_passenger_count(schedule, day_name, is_holiday)
            
            record = {
                "record_id": record_id,
                "schedule_id": schedule['schedule_id'],
                "train_number": schedule['train_number'],
                "route_id": schedule['route_id'],
                "origin_name": schedule['origin_name'],
                "destination_name": schedule['destination_name'],
                "passenger_count": passenger_count,
                "capacity": schedule['capacity'],
                "occupancy_rate": round(passenger_count / schedule['capacity'], 2),
                "booking_date": booking_date.strftime("%Y-%m-%d"),
                "travel_date": current_date.strftime("%Y-%m-%d"),
                "day_of_week": day_name,
                "departure_time": schedule['departure_time'],
                "train_type": schedule['train_type']
            }
            
            passengers.append(record)
            record_id += 1
    
    return passengers

def save_passengers(passengers):
    """Save passenger data to JSON file"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'passengers.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(passengers, f, indent=2, ensure_ascii=False)
    
    # Statistics
    total_records = len(passengers)
    total_passengers = sum(p['passenger_count'] for p in passengers)
    avg_occupancy = sum(p['occupancy_rate'] for p in passengers) / total_records
    
    print(f"[OK] Generated {total_records} passenger flow records (6 months)")
    print(f"  - Total passengers: {total_passengers:,}")
    print(f"  - Average occupancy: {avg_occupancy:.1%}")
    print(f"[OK] Saved to: {output_file}")
    return passengers

if __name__ == "__main__":
    # Load schedules
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    with open(os.path.join(data_dir, 'schedules.json'), 'r', encoding='utf-8') as f:
        schedules = json.load(f)
    
    # Generate 6 months of passenger data
    start_date = datetime.now() - timedelta(days=180)
    passengers = generate_passengers_for_period(schedules, start_date, days=180)
    save_passengers(passengers)
