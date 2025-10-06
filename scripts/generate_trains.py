"""
Generate synthetic train data for Moroccan railway network
"""
import json
import os

# Train types based on ONCF fleet
TRAIN_TYPES = {
    "Al Boraq": {
        "speed_kmh": 320,
        "capacity": 533,
        "count": 12,
        "pricing": "premium"
    },
    "TNR": {
        "speed_kmh": 160,
        "capacity": 400,
        "count": 35,
        "pricing": "standard"
    },
    "Regular": {
        "speed_kmh": 100,
        "capacity": 300,
        "count": 33,
        "pricing": "economy"
    }
}

def generate_trains():
    """Generate train fleet data"""
    trains = []
    train_id = 1
    
    for train_type, specs in TRAIN_TYPES.items():
        for i in range(specs['count']):
            train = {
                "train_id": train_id,
                "train_number": f"{train_type[:3].upper()}{train_id:04d}",
                "train_type": train_type,
                "speed_kmh": specs['speed_kmh'],
                "capacity": specs['capacity'],
                "pricing_tier": specs['pricing'],
                "operational_status": "active"
            }
            trains.append(train)
            train_id += 1
    
    return trains

def save_trains(trains):
    """Save trains to JSON file"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'trains.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(trains, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Generated {len(trains)} trains")
    print(f"  - Al Boraq (high-speed): {TRAIN_TYPES['Al Boraq']['count']}")
    print(f"  - TNR (fast): {TRAIN_TYPES['TNR']['count']}")
    print(f"  - Regular: {TRAIN_TYPES['Regular']['count']}")
    print(f"[OK] Saved to: {output_file}")
    return trains

if __name__ == "__main__":
    trains = generate_trains()
    save_trains(trains)
