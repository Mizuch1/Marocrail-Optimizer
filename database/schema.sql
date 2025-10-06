-- MarocRail-Optimizer Database Schema
-- SQLite database for train scheduling and delay prediction

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Stations Table
CREATE TABLE IF NOT EXISTS stations (
    station_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    platform_count INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    is_major BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Routes Table
CREATE TABLE IF NOT EXISTS routes (
    route_id INTEGER PRIMARY KEY,
    origin_station_id INTEGER NOT NULL,
    destination_station_id INTEGER NOT NULL,
    distance_km REAL NOT NULL,
    typical_duration_minutes INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (origin_station_id) REFERENCES stations(station_id),
    FOREIGN KEY (destination_station_id) REFERENCES stations(station_id),
    UNIQUE(origin_station_id, destination_station_id)
);

-- Trains Table
CREATE TABLE IF NOT EXISTS trains (
    train_id INTEGER PRIMARY KEY,
    train_number TEXT NOT NULL UNIQUE,
    train_type TEXT NOT NULL CHECK(train_type IN ('Al Boraq', 'TNR', 'Regular')),
    speed_kmh INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    pricing_tier TEXT NOT NULL CHECK(pricing_tier IN ('premium', 'standard', 'economy')),
    operational_status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schedules Table
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INTEGER PRIMARY KEY,
    train_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    platform INTEGER NOT NULL,
    day_of_week TEXT NOT NULL CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'on-time', 'delayed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (train_id) REFERENCES trains(train_id),
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

-- Delays Table
CREATE TABLE IF NOT EXISTS delays (
    delay_id INTEGER PRIMARY KEY,
    schedule_id INTEGER NOT NULL,
    delay_minutes INTEGER NOT NULL,
    delay_reason TEXT NOT NULL CHECK(delay_reason IN ('weather', 'technical', 'passenger', 'maintenance', 'cascade')),
    weather_condition TEXT NOT NULL CHECK(weather_condition IN ('sunny', 'cloudy', 'rainy', 'foggy', 'hot')),
    timestamp TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
);

-- Passengers Table
CREATE TABLE IF NOT EXISTS passengers (
    record_id INTEGER PRIMARY KEY,
    schedule_id INTEGER NOT NULL,
    passenger_count INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    travel_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_routes_origin ON routes(origin_station_id);
CREATE INDEX IF NOT EXISTS idx_routes_destination ON routes(destination_station_id);
CREATE INDEX IF NOT EXISTS idx_schedules_train ON schedules(train_id);
CREATE INDEX IF NOT EXISTS idx_schedules_route ON schedules(route_id);
CREATE INDEX IF NOT EXISTS idx_schedules_day ON schedules(day_of_week);
CREATE INDEX IF NOT EXISTS idx_schedules_departure ON schedules(departure_time);
CREATE INDEX IF NOT EXISTS idx_delays_schedule ON delays(schedule_id);
CREATE INDEX IF NOT EXISTS idx_delays_reason ON delays(delay_reason);
CREATE INDEX IF NOT EXISTS idx_delays_timestamp ON delays(timestamp);
CREATE INDEX IF NOT EXISTS idx_passengers_schedule ON passengers(schedule_id);
CREATE INDEX IF NOT EXISTS idx_passengers_travel_date ON passengers(travel_date);

-- Views for common queries

-- View: Schedule Details (joins schedules with trains and routes)
CREATE VIEW IF NOT EXISTS schedule_details AS
SELECT 
    s.schedule_id,
    s.train_id,
    t.train_number,
    t.train_type,
    t.capacity,
    s.route_id,
    r.distance_km,
    r.typical_duration_minutes,
    st_origin.name as origin_station,
    st_origin.city as origin_city,
    st_dest.name as destination_station,
    st_dest.city as destination_city,
    s.departure_time,
    s.arrival_time,
    s.platform,
    s.day_of_week,
    s.status
FROM schedules s
JOIN trains t ON s.train_id = t.train_id
JOIN routes r ON s.route_id = r.route_id
JOIN stations st_origin ON r.origin_station_id = st_origin.station_id
JOIN stations st_dest ON r.destination_station_id = st_dest.station_id;

-- View: Delay Statistics
CREATE VIEW IF NOT EXISTS delay_statistics AS
SELECT 
    d.delay_reason,
    COUNT(*) as delay_count,
    AVG(d.delay_minutes) as avg_delay_minutes,
    MAX(d.delay_minutes) as max_delay_minutes,
    d.weather_condition,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM delays) as percentage
FROM delays d
GROUP BY d.delay_reason, d.weather_condition;

-- View: Route Performance
CREATE VIEW IF NOT EXISTS route_performance AS
SELECT 
    r.route_id,
    st_origin.name as origin_station,
    st_dest.name as destination_station,
    r.distance_km,
    COUNT(DISTINCT s.schedule_id) as total_schedules,
    COUNT(d.delay_id) as total_delays,
    ROUND(COUNT(d.delay_id) * 100.0 / COUNT(DISTINCT s.schedule_id), 2) as delay_rate,
    AVG(d.delay_minutes) as avg_delay_minutes
FROM routes r
JOIN stations st_origin ON r.origin_station_id = st_origin.station_id
JOIN stations st_dest ON r.destination_station_id = st_dest.station_id
LEFT JOIN schedules s ON r.route_id = s.route_id
LEFT JOIN delays d ON s.schedule_id = d.schedule_id
GROUP BY r.route_id;
