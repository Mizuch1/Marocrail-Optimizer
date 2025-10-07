"""
Flask backend API for MarocRail-Optimizer
"""
from flask import Flask, jsonify, request, render_template
import sqlite3
import os
from datetime import datetime
from scripts.optimizer import ScheduleOptimizer
import joblib

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'marocrail.db')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/schedules')
def schedules_page():
    """Schedules page"""
    return render_template('schedules.html')

@app.route('/analytics')
def analytics_page():
    """Analytics page"""
    return render_template('analytics.html')

@app.route('/predict')
def predict_page():
    """Prediction page"""
    return render_template('predict.html')

@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Get all stations"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT station_id, name, city, latitude, longitude, 
               platform_count, capacity, is_major
        FROM stations
        ORDER BY name
    """)
    
    stations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(stations),
        'data': stations
    })

@app.route('/api/routes', methods=['GET'])
def get_routes():
    """Get all routes"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            r.route_id,
            r.distance_km,
            r.typical_duration_minutes,
            s1.name as origin_name,
            s1.city as origin_city,
            s2.name as destination_name,
            s2.city as destination_city
        FROM routes r
        JOIN stations s1 ON r.origin_station_id = s1.station_id
        JOIN stations s2 ON r.destination_station_id = s2.station_id
        ORDER BY s1.name, s2.name
    """)
    
    routes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(routes),
        'data': routes
    })

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get schedules with filters"""
    day = request.args.get('day', 'Monday')
    route_id = request.args.get('route_id')
    status = request.args.get('status')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            s.schedule_id,
            s.departure_time,
            s.arrival_time,
            s.platform,
            s.day_of_week,
            s.status,
            t.train_number,
            t.train_type,
            t.capacity,
            st1.name as origin_station,
            st2.name as destination_station,
            r.distance_km
        FROM schedules s
        JOIN trains t ON s.train_id = t.train_id
        JOIN routes r ON s.route_id = r.route_id
        JOIN stations st1 ON r.origin_station_id = st1.station_id
        JOIN stations st2 ON r.destination_station_id = st2.station_id
        WHERE s.day_of_week = ?
    """
    
    params = [day]
    
    if route_id:
        query += " AND s.route_id = ?"
        params.append(route_id)
    
    if status:
        query += " AND s.status = ?"
        params.append(status)
    
    query += " ORDER BY s.departure_time LIMIT 100"
    
    cursor.execute(query, params)
    schedules = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(schedules),
        'filters': {'day': day, 'route_id': route_id, 'status': status},
        'data': schedules
    })

@app.route('/api/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule_detail(schedule_id):
    """Get detailed schedule info"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            s.schedule_id,
            s.departure_time,
            s.arrival_time,
            s.platform,
            s.day_of_week,
            s.status,
            t.train_id,
            t.train_number,
            t.train_type,
            t.capacity,
            t.speed_kmh,
            r.route_id,
            r.distance_km,
            r.typical_duration_minutes,
            st1.station_id as origin_station_id,
            st1.name as origin_station,
            st1.city as origin_city,
            st2.station_id as destination_station_id,
            st2.name as destination_station,
            st2.city as destination_city
        FROM schedules s
        JOIN trains t ON s.train_id = t.train_id
        JOIN routes r ON s.route_id = r.route_id
        JOIN stations st1 ON r.origin_station_id = st1.station_id
        JOIN stations st2 ON r.destination_station_id = st2.station_id
        WHERE s.schedule_id = ?
    """, (schedule_id,))
    
    schedule = cursor.fetchone()
    
    if not schedule:
        conn.close()
        return jsonify({'success': False, 'error': 'Schedule not found'}), 404
    
    schedule_data = dict(schedule)
    
    cursor.execute("""
        SELECT delay_minutes, delay_reason, weather_condition, timestamp
        FROM delays
        WHERE schedule_id = ?
        ORDER BY timestamp DESC
        LIMIT 10
    """, (schedule_id,))
    
    delays = [dict(row) for row in cursor.fetchall()]
    schedule_data['recent_delays'] = delays
    
    conn.close()
    
    return jsonify({
        'success': True,
        'data': schedule_data
    })

@app.route('/api/delays', methods=['GET'])
def get_delays():
    """Get delay statistics"""
    reason = request.args.get('reason')
    limit = int(request.args.get('limit', 50))
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            d.delay_id,
            d.delay_minutes,
            d.delay_reason,
            d.weather_condition,
            d.timestamp,
            s.departure_time,
            t.train_number,
            st1.name as origin_station,
            st2.name as destination_station
        FROM delays d
        JOIN schedules s ON d.schedule_id = s.schedule_id
        JOIN trains t ON s.train_id = t.train_id
        JOIN routes r ON s.route_id = r.route_id
        JOIN stations st1 ON r.origin_station_id = st1.station_id
        JOIN stations st2 ON r.destination_station_id = st2.station_id
    """
    
    params = []
    if reason:
        query += " WHERE d.delay_reason = ?"
        params.append(reason)
    
    query += " ORDER BY d.timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    delays = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(delays),
        'data': delays
    })

@app.route('/api/analytics/delays', methods=['GET'])
def get_delay_analytics():
    """Get delay analytics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            delay_reason,
            COUNT(*) as count,
            AVG(delay_minutes) as avg_delay,
            MAX(delay_minutes) as max_delay
        FROM delays
        GROUP BY delay_reason
        ORDER BY count DESC
    """)
    
    by_reason = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT 
            strftime('%H', timestamp) as hour,
            COUNT(*) as count,
            AVG(delay_minutes) as avg_delay
        FROM delays
        GROUP BY hour
        ORDER BY hour
    """)
    
    by_hour = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT 
            weather_condition,
            COUNT(*) as count,
            AVG(delay_minutes) as avg_delay
        FROM delays
        GROUP BY weather_condition
        ORDER BY count DESC
    """)
    
    by_weather = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'data': {
            'by_reason': by_reason,
            'by_hour': by_hour,
            'by_weather': by_weather
        }
    })

@app.route('/api/analytics/overview', methods=['GET'])
def get_overview():
    """Get overview statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM stations")
    total_stations = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM routes")
    total_routes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM trains")
    total_trains = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schedules")
    total_schedules = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM delays")
    total_delays = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(delay_minutes) FROM delays")
    avg_delay = cursor.fetchone()[0]
    
    on_time_rate = ((total_schedules * 7 - total_delays) / (total_schedules * 7)) * 100
    
    conn.close()
    
    return jsonify({
        'success': True,
        'data': {
            'total_stations': total_stations,
            'total_routes': total_routes,
            'total_trains': total_trains,
            'total_schedules': total_schedules,
            'total_delays': total_delays,
            'avg_delay_minutes': round(avg_delay, 2) if avg_delay else 0,
            'on_time_rate': round(on_time_rate, 2)
        }
    })

@app.route('/api/predict', methods=['POST'])
def predict_delay():
    """Predict delay for given parameters"""
    data = request.get_json()
    
    required = ['route_id', 'hour', 'day_of_week', 'weather']
    if not all(k in data for k in required):
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
    
    try:
        classifier = joblib.load(os.path.join(MODEL_DIR, 'delay_classifier.pkl'))
        regressor = joblib.load(os.path.join(MODEL_DIR, 'delay_regressor.pkl'))
        feature_cols = joblib.load(os.path.join(MODEL_DIR, 'feature_columns.pkl'))
        
        import pandas as pd
        
        features = {}
        features['hour'] = int(data['hour'])
        features['day_of_week'] = int(data['day_of_week'])
        features['month'] = int(data.get('month', 6))
        features['is_peak_hour'] = (6 <= features['hour'] <= 9) or (17 <= features['hour'] <= 20)
        features['is_weekend'] = features['day_of_week'] in [0, 6]
        
        for weather in ['cloudy', 'foggy', 'hot', 'rainy', 'sunny']:
            features[f'weather_{weather}'] = 1 if data['weather'] == weather else 0
        
        features['train_type_code'] = int(data.get('train_type_code', 2))
        features['capacity'] = int(data.get('capacity', 400))
        features['distance_km'] = float(data.get('distance_km', 100))
        features['typical_duration_minutes'] = int(data.get('duration', 90))
        features['route_avg_delay'] = 15.0
        features['route_std_delay'] = 5.0
        
        season = 'summer' if features['month'] in [6, 7, 8] else 'winter'
        for s in ['autumn', 'spring', 'summer', 'winter']:
            features[f'season_{s}'] = 1 if s == season else 0
        
        df = pd.DataFrame([features])
        X = df[feature_cols].fillna(0)
        
        delay_prob = classifier.predict_proba(X)[0][1]
        
        result = {
            'delay_probability': round(float(delay_prob), 4),
            'risk_level': 'high' if delay_prob > 0.7 else 'medium' if delay_prob > 0.4 else 'low',
            'will_delay': bool(delay_prob > 0.5)
        }
        
        if delay_prob > 0.5:
            delay_minutes = regressor.predict(X)[0]
            result['estimated_delay_minutes'] = round(float(delay_minutes), 1)
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/optimize', methods=['POST'])
def optimize_schedule():
    """Run schedule optimization"""
    data = request.get_json()
    day = data.get('day', 'Monday')
    
    try:
        optimizer = ScheduleOptimizer()
        
        schedules = optimizer.load_schedules(day)
        schedules = optimizer.predict_delays(schedules)
        conflicts = optimizer.detect_conflicts(schedules)
        optimized, changes = optimizer.optimize_schedule(schedules, conflicts)
        metrics = optimizer.calculate_metrics(schedules, optimized, changes)
        
        optimizer.close()
        
        return jsonify({
            'success': True,
            'data': {
                'metrics': metrics,
                'changes': changes[:20],
                'conflicts': conflicts[:10]
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
