"""
Generate synthetic route data for Moroccan railway network
"""
import json
import os
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return round(R * c, 2)

# Route definitions: (origin_id, destination_id, typical_duration_minutes)
ROUTE_DEFINITIONS = [
    # Casablanca routes
    (1, 3, 50),    # Casa-Port to Rabat-Ville
    (2, 3, 55),    # Casa-Voyageurs to Rabat-Ville
    (2, 8, 180),   # Casa-Voyageurs to Marrakech
    (1, 9, 270),   # Casa-Port to Tanger
    (2, 7, 210),   # Casa-Voyageurs to Fès
    
    # Rabat routes
    (3, 5, 25),    # Rabat-Ville to Kenitra
    (3, 7, 150),   # Rabat-Ville to Fès
    (3, 9, 180),   # Rabat-Ville to Tanger
    (4, 5, 30),    # Rabat-Agdal to Kenitra
    
    # Kenitra routes
    (5, 6, 90),    # Kenitra to Meknès
    (5, 9, 150),   # Kenitra to Tanger
    
    # Fès routes
    (7, 6, 60),    # Fès to Meknès
    (7, 10, 180),  # Fès to Oujda
    (7, 9, 240),   # Fès to Tanger
    
    # Other routes
    (6, 10, 240),  # Meknès to Oujda
    (8, 3, 200),   # Marrakech to Rabat-Ville
    
    # Reverse routes (bidirectional)
    (3, 1, 50),    # Rabat-Ville to Casa-Port
    (3, 2, 55),    # Rabat-Ville to Casa-Voyageurs
    (8, 2, 180),   # Marrakech to Casa-Voyageurs
    (9, 1, 270),   # Tanger to Casa-Port
    (7, 2, 210),   # Fès to Casa-Voyageurs
    (5, 3, 25),    # Kenitra to Rabat-Ville
    (7, 3, 150),   # Fès to Rabat-Ville
    (9, 3, 180),   # Tanger to Rabat-Ville
    (9, 5, 150),   # Tanger to Kenitra
]

def generate_routes(stations):
    """Generate route data based on station coordinates"""
    routes = []
    route_id = 1
    
    for origin_id, dest_id, duration in ROUTE_DEFINITIONS:
        # Find origin and destination stations
        origin = next(s for s in stations if s['station_id'] == origin_id)
        dest = next(s for s in stations if s['station_id'] == dest_id)
        
        # Calculate distance
        distance = calculate_distance(
            origin['latitude'], origin['longitude'],
            dest['latitude'], dest['longitude']
        )
        
        route = {
            "route_id": route_id,
            "origin_station_id": origin_id,
            "origin_name": origin['name'],
            "destination_station_id": dest_id,
            "destination_name": dest['name'],
            "distance_km": distance,
            "typical_duration_minutes": duration
        }
        
        routes.append(route)
        route_id += 1
    
    return routes

def save_routes(routes):
    """Save routes to JSON file"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'routes.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(routes, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Generated {len(routes)} routes")
    print(f"[OK] Saved to: {output_file}")
    return routes

if __name__ == "__main__":
    # Load stations
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    stations_file = os.path.join(data_dir, 'stations.json')
    
    with open(stations_file, 'r', encoding='utf-8') as f:
        stations = json.load(f)
    
    routes = generate_routes(stations)
    save_routes(routes)
