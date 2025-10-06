"""
Generate synthetic station data for Moroccan railway network
"""
import json
import os

# Moroccan railway stations with realistic coordinates and details
STATIONS = [
    {
        "station_id": 1,
        "name": "Casa-Port",
        "city": "Casablanca",
        "latitude": 33.6061,
        "longitude": -7.6164,
        "platform_count": 8,
        "capacity": 5000,
        "is_major": True
    },
    {
        "station_id": 2,
        "name": "Casa-Voyageurs",
        "city": "Casablanca",
        "latitude": 33.5900,
        "longitude": -7.5898,
        "platform_count": 12,
        "capacity": 8000,
        "is_major": True
    },
    {
        "station_id": 3,
        "name": "Rabat-Ville",
        "city": "Rabat",
        "latitude": 34.0174,
        "longitude": -6.8340,
        "platform_count": 10,
        "capacity": 6000,
        "is_major": True
    },
    {
        "station_id": 4,
        "name": "Rabat-Agdal",
        "city": "Rabat",
        "latitude": 33.9667,
        "longitude": -6.8577,
        "platform_count": 6,
        "capacity": 3000,
        "is_major": False
    },
    {
        "station_id": 5,
        "name": "Kenitra",
        "city": "Kenitra",
        "latitude": 34.2610,
        "longitude": -6.5802,
        "platform_count": 6,
        "capacity": 3500,
        "is_major": True
    },
    {
        "station_id": 6,
        "name": "Meknès",
        "city": "Meknès",
        "latitude": 33.8935,
        "longitude": -5.5473,
        "platform_count": 5,
        "capacity": 2500,
        "is_major": False
    },
    {
        "station_id": 7,
        "name": "Fès",
        "city": "Fès",
        "latitude": 34.0331,
        "longitude": -5.0003,
        "platform_count": 8,
        "capacity": 4000,
        "is_major": True
    },
    {
        "station_id": 8,
        "name": "Marrakech",
        "city": "Marrakech",
        "latitude": 31.6295,
        "longitude": -7.9811,
        "platform_count": 7,
        "capacity": 4500,
        "is_major": True
    },
    {
        "station_id": 9,
        "name": "Tanger-Ville",
        "city": "Tanger",
        "latitude": 35.7595,
        "longitude": -5.8340,
        "platform_count": 6,
        "capacity": 3500,
        "is_major": True
    },
    {
        "station_id": 10,
        "name": "Oujda",
        "city": "Oujda",
        "latitude": 34.6867,
        "longitude": -1.9114,
        "platform_count": 5,
        "capacity": 2000,
        "is_major": False
    }
]

def generate_stations():
    """Generate station data and save to JSON"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'stations.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(STATIONS, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Generated {len(STATIONS)} stations")
    print(f"[OK] Saved to: {output_file}")
    return STATIONS

if __name__ == "__main__":
    generate_stations()
