"""
Generate synthetic historical delay data with realistic patterns
"""
import json
import os
import random
from datetime import datetime, timedelta

# Delay reasons and their characteristics
DELAY_REASONS = {
    "weather": {
        "probability": 0.15,
        "min_delay": 5,
        "max_delay": 30,
        "seasons": ["winter", "autumn"]  # More common in rainy seasons
    },
    "technical": {
        "probability": 0.08,
        "min_delay": 10,
        "max_delay": 60,
        "random": True
    },
    "passenger": {
        "probability": 0.20,
        "min_delay": 2,
        "max_delay": 10,
        "peak_hours": True  # More common during peak hours
    },
    "maintenance": {
        "probability": 0.05,
        "min_delay": 15,
        "max_delay": 45,
        "weekend": True  # More common on weekends
    },
    "cascade": {
        "probability": 0.10,
        "min_delay": 10,
        "max_delay": 40,
        "depends_on_previous": True
    }
}

WEATHER_CONDITIONS = ["sunny", "cloudy", "rainy", "foggy", "hot"]
SEASON_MONTHS = {
    "winter": [12, 1, 2],
    "spring": [3, 4, 5],
    "summer": [6, 7, 8],
    "autumn": [9, 10, 11]
}

def get_season(month):
    """Get season from month"""
    for season, months in SEASON_MONTHS.items():
        if month in months:
            return season
    return "spring"

def is_peak_hour(hour):
    """Check if hour is during peak time"""
    return (6 <= hour <= 9) or (17 <= hour <= 20)

def get_weather_for_season(season):
    """Get realistic weather for season"""
    if season == "winter":
        return random.choices(["rainy", "cloudy", "foggy", "sunny"], weights=[0.4, 0.3, 0.2, 0.1])[0]
    elif season == "summer":
        return random.choices(["sunny", "hot", "cloudy"], weights=[0.5, 0.4, 0.1])[0]
    elif season == "autumn":
        return random.choices(["rainy", "cloudy", "sunny"], weights=[0.35, 0.35, 0.3])[0]
    else:  # spring
        return random.choices(["sunny", "cloudy", "rainy"], weights=[0.5, 0.3, 0.2])[0]

def should_delay_occur(schedule, weather, season, is_weekend, previous_delays):
    """Determine if a delay should occur and what type"""
    hour = int(schedule['departure_time'].split(':')[0])
    
    # Check each delay reason
    for reason, specs in DELAY_REASONS.items():
        prob = specs['probability']
        
        # Adjust probability based on conditions
        if reason == "weather":
            if season in specs.get('seasons', []) and weather in ["rainy", "foggy"]:
                prob *= 2.5
            elif weather == "hot":
                prob *= 1.3
            else:
                prob *= 0.3
        
        elif reason == "passenger":
            if is_peak_hour(hour):
                prob *= 2.0
        
        elif reason == "maintenance":
            if is_weekend:
                prob *= 2.0
            else:
                prob *= 0.5
        
        elif reason == "cascade":
            # Cascade delays happen when previous trains on same route are delayed
            if previous_delays > 0:
                prob *= (1 + previous_delays * 0.5)
        
        # Roll for delay
        if random.random() < prob:
            delay_minutes = random.randint(specs['min_delay'], specs['max_delay'])
            return reason, delay_minutes
    
    return None, 0

def generate_delays_for_period(schedules, start_date, days=180):
    """Generate 6 months of delay history"""
    delays = []
    delay_id = 1
    
    # Track delays by route for cascade effect
    route_delays = {}
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        day_name = current_date.strftime("%A")
        is_weekend = day_name in ["Saturday", "Sunday"]
        month = current_date.month
        season = get_season(month)
        
        # Daily weather
        weather = get_weather_for_season(season)
        
        # Reset route delays at start of day
        route_delays = {}
        
        # Get schedules for this day
        day_schedules = [s for s in schedules if s['day_of_week'] == day_name]
        
        # Sort by departure time to handle cascade effects
        day_schedules.sort(key=lambda x: x['departure_time'])
        
        for schedule in day_schedules:
            route_id = schedule['route_id']
            previous_route_delays = route_delays.get(route_id, 0)
            
            # Check if delay occurs
            reason, delay_minutes = should_delay_occur(
                schedule, weather, season, is_weekend, previous_route_delays
            )
            
            if reason:
                # Create delay record
                timestamp = datetime.combine(current_date, 
                    datetime.strptime(schedule['departure_time'], "%H:%M").time())
                
                delay = {
                    "delay_id": delay_id,
                    "schedule_id": schedule['schedule_id'],
                    "train_number": schedule['train_number'],
                    "route_id": route_id,
                    "origin_name": schedule['origin_name'],
                    "destination_name": schedule['destination_name'],
                    "delay_minutes": delay_minutes,
                    "delay_reason": reason,
                    "weather_condition": weather,
                    "timestamp": timestamp.isoformat(),
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day_of_week": day_name,
                    "hour": int(schedule['departure_time'].split(':')[0]),
                    "season": season,
                    "resolved": random.choice([True, True, True, False])  # 75% resolved
                }
                
                delays.append(delay)
                delay_id += 1
                
                # Track for cascade effect
                route_delays[route_id] = route_delays.get(route_id, 0) + 1
    
    return delays

def save_delays(delays):
    """Save delays to JSON file"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'delays.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(delays, f, indent=2, ensure_ascii=False)
    
    # Statistics
    total_delays = len(delays)
    by_reason = {}
    for delay in delays:
        reason = delay['delay_reason']
        by_reason[reason] = by_reason.get(reason, 0) + 1
    
    print(f"[OK] Generated {total_delays} delay records (6 months)")
    print(f"  Breakdown by reason:")
    for reason, count in sorted(by_reason.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_delays) * 100
        print(f"    - {reason}: {count} ({pct:.1f}%)")
    print(f"[OK] Saved to: {output_file}")
    return delays

if __name__ == "__main__":
    # Load schedules
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    with open(os.path.join(data_dir, 'schedules.json'), 'r', encoding='utf-8') as f:
        schedules = json.load(f)
    
    # Generate 6 months of delay history (starting 6 months ago)
    start_date = datetime.now() - timedelta(days=180)
    delays = generate_delays_for_period(schedules, start_date, days=180)
    save_delays(delays)
