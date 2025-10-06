"""
Simplified schedule optimization using heuristic rules
"""
import sqlite3
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'marocrail.db')
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')

class ScheduleOptimizer:
    def __init__(self):
        self.classifier = joblib.load(os.path.join(MODEL_DIR, 'delay_classifier.pkl'))
        self.regressor = joblib.load(os.path.join(MODEL_DIR, 'delay_regressor.pkl'))
        self.feature_cols = joblib.load(os.path.join(MODEL_DIR, 'feature_columns.pkl'))
        self.conn = sqlite3.connect(DB_PATH)
    
    def load_schedules(self, day_of_week='Monday'):
        """Load schedules for optimization"""
        query = """
        SELECT 
            s.schedule_id,
            s.train_id,
            t.train_number,
            t.train_type,
            t.capacity,
            s.route_id,
            r.origin_station_id,
            r.destination_station_id,
            r.distance_km,
            r.typical_duration_minutes,
            s.departure_time,
            s.arrival_time,
            s.platform,
            s.day_of_week
        FROM schedules s
        JOIN trains t ON s.train_id = t.train_id
        JOIN routes r ON s.route_id = r.route_id
        WHERE s.day_of_week = ?
        ORDER BY s.departure_time
        """
        return pd.read_sql_query(query, self.conn, params=(day_of_week,))
    
    def predict_delays(self, schedules):
        """Predict delay probability for each schedule"""
        features = self._prepare_features(schedules)
        delay_prob = self.classifier.predict_proba(features)[:, 1]
        schedules['delay_probability'] = delay_prob
        schedules['high_risk'] = delay_prob > 0.7
        return schedules
    
    def _prepare_features(self, schedules):
        """Prepare features for ML model"""
        df = schedules.copy()
        
        df['hour'] = pd.to_datetime(df['departure_time'], format='%H:%M').dt.hour
        df['day_of_week'] = pd.to_datetime('2024-01-01').dayofweek
        df['month'] = 6
        df['is_peak_hour'] = ((df['hour'] >= 6) & (df['hour'] <= 9)) | ((df['hour'] >= 17) & (df['hour'] <= 20))
        df['is_weekend'] = False
        
        for weather in ['cloudy', 'foggy', 'hot', 'rainy', 'sunny']:
            df[f'weather_{weather}'] = 1 if weather == 'sunny' else 0
        
        train_type_map = {'Al Boraq': 3, 'TNR': 2, 'Regular': 1}
        df['train_type_code'] = df['train_type'].map(train_type_map)
        
        df['route_avg_delay'] = 15.0
        df['route_std_delay'] = 5.0
        
        for season in ['autumn', 'spring', 'summer', 'winter']:
            df[f'season_{season}'] = 1 if season == 'summer' else 0
        
        return df[self.feature_cols].fillna(0)
    
    def detect_conflicts(self, schedules):
        """Find scheduling conflicts"""
        conflicts = []
        
        schedules['dep_minutes'] = pd.to_datetime(schedules['departure_time'], format='%H:%M').dt.hour * 60 + \
                                   pd.to_datetime(schedules['departure_time'], format='%H:%M').dt.minute
        
        # Platform conflicts
        for station_id in schedules['origin_station_id'].unique():
            station_schedules = schedules[schedules['origin_station_id'] == station_id].copy()
            
            for platform in station_schedules['platform'].unique():
                platform_trains = station_schedules[station_schedules['platform'] == platform].sort_values('dep_minutes')
                
                for i in range(len(platform_trains) - 1):
                    current = platform_trains.iloc[i]
                    next_train = platform_trains.iloc[i + 1]
                    
                    time_diff = next_train['dep_minutes'] - current['dep_minutes']
                    
                    if time_diff < 10:
                        conflicts.append({
                            'type': 'platform_conflict',
                            'station_id': station_id,
                            'platform': platform,
                            'train_1': current['train_number'],
                            'train_2': next_train['train_number'],
                            'time_gap': time_diff,
                            'schedule_ids': [current['schedule_id'], next_train['schedule_id']]
                        })
        
        # Train conflicts
        train_usage = schedules.groupby('train_id').agg({
            'schedule_id': 'count',
            'dep_minutes': ['min', 'max']
        }).reset_index()
        train_usage.columns = ['train_id', 'trip_count', 'first_dep', 'last_dep']
        
        for _, train in train_usage.iterrows():
            train_schedules = schedules[schedules['train_id'] == train['train_id']].sort_values('dep_minutes')
            
            for i in range(len(train_schedules) - 1):
                current = train_schedules.iloc[i]
                next_trip = train_schedules.iloc[i + 1]
                
                turnaround_time = next_trip['dep_minutes'] - (current['dep_minutes'] + current['typical_duration_minutes'])
                
                if turnaround_time < 30:
                    conflicts.append({
                        'type': 'turnaround_conflict',
                        'train_id': train['train_id'],
                        'train_number': current['train_number'],
                        'turnaround_time': turnaround_time,
                        'schedule_ids': [current['schedule_id'], next_trip['schedule_id']]
                    })
        
        return conflicts
    
    def optimize_schedule(self, schedules, conflicts):
        """Apply optimization rules"""
        optimized = schedules.copy()
        changes = []
        
        # Rule 1: Adjust high-risk trains (add buffer time)
        high_risk = optimized[optimized['high_risk'] == True]
        for idx, train in high_risk.iterrows():
            if train['delay_probability'] > 0.8:
                changes.append({
                    'schedule_id': train['schedule_id'],
                    'action': 'add_buffer',
                    'reason': f"High delay risk ({train['delay_probability']:.0%})",
                    'details': 'Add 10 min buffer'
                })
        
        # Rule 2: Resolve platform conflicts
        for conflict in conflicts:
            if conflict['type'] == 'platform_conflict':
                schedule_id = conflict['schedule_ids'][1]
                changes.append({
                    'schedule_id': schedule_id,
                    'action': 'delay_departure',
                    'reason': 'Platform conflict',
                    'details': f"Delay by {15 - conflict['time_gap']} minutes"
                })
        
        # Rule 3: Resolve turnaround conflicts
        for conflict in conflicts:
            if conflict['type'] == 'turnaround_conflict':
                schedule_id = conflict['schedule_ids'][1]
                changes.append({
                    'schedule_id': schedule_id,
                    'action': 'delay_departure',
                    'reason': 'Insufficient turnaround',
                    'details': f"Delay by {35 - conflict['turnaround_time']} minutes"
                })
        
        # Rule 4: Reassign platforms for conflicts
        platform_conflicts = [c for c in conflicts if c['type'] == 'platform_conflict']
        for conflict in platform_conflicts[:5]:
            schedule_id = conflict['schedule_ids'][1]
            station_id = conflict['station_id']
            
            station_schedules = optimized[optimized['origin_station_id'] == station_id]
            used_platforms = station_schedules['platform'].unique()
            
            max_platform = station_schedules['platform'].max()
            if max_platform < 8:
                new_platform = max_platform + 1
                changes.append({
                    'schedule_id': schedule_id,
                    'action': 'reassign_platform',
                    'reason': 'Platform conflict resolution',
                    'details': f"Move to platform {new_platform}"
                })
        
        return optimized, changes
    
    def calculate_metrics(self, original_schedules, optimized_schedules, changes):
        """Calculate optimization impact"""
        original_risk = original_schedules['high_risk'].sum()
        optimized_risk = original_risk - len([c for c in changes if c['action'] == 'add_buffer'])
        
        metrics = {
            'total_schedules': len(original_schedules),
            'high_risk_trains': int(original_risk),
            'changes_applied': len(changes),
            'estimated_risk_reduction': max(0, original_risk - optimized_risk),
            'conflicts_detected': len(changes),
            'platform_reassignments': len([c for c in changes if c['action'] == 'reassign_platform']),
            'time_adjustments': len([c for c in changes if c['action'] == 'delay_departure'])
        }
        
        return metrics
    
    def close(self):
        self.conn.close()

def main():
    print("="*60)
    print("  MarocRail-Optimizer - Schedule Optimization")
    print("="*60)
    
    optimizer = ScheduleOptimizer()
    
    print("\n[1/5] Loading schedules...")
    schedules = optimizer.load_schedules('Monday')
    print(f"[OK] Loaded {len(schedules)} schedules for Monday")
    
    print("\n[2/5] Predicting delays...")
    schedules = optimizer.predict_delays(schedules)
    high_risk_count = schedules['high_risk'].sum()
    print(f"[OK] Identified {high_risk_count} high-risk trains")
    
    print("\n[3/5] Detecting conflicts...")
    conflicts = optimizer.detect_conflicts(schedules)
    print(f"[OK] Found {len(conflicts)} scheduling conflicts")
    
    if conflicts:
        print("\n  Conflict breakdown:")
        conflict_types = {}
        for c in conflicts:
            conflict_types[c['type']] = conflict_types.get(c['type'], 0) + 1
        for ctype, count in conflict_types.items():
            print(f"    - {ctype}: {count}")
    
    print("\n[4/5] Applying optimization rules...")
    optimized, changes = optimizer.optimize_schedule(schedules, conflicts)
    print(f"[OK] Generated {len(changes)} optimization changes")
    
    print("\n[5/5] Calculating impact...")
    metrics = optimizer.calculate_metrics(schedules, optimized, changes)
    
    print("\n" + "="*60)
    print("  Optimization Results")
    print("="*60)
    print(f"  Total schedules:          {metrics['total_schedules']}")
    print(f"  High-risk trains:         {metrics['high_risk_trains']}")
    print(f"  Conflicts detected:       {metrics['conflicts_detected']}")
    print(f"  Changes proposed:         {metrics['changes_applied']}")
    print(f"  Platform reassignments:   {metrics['platform_reassignments']}")
    print(f"  Time adjustments:         {metrics['time_adjustments']}")
    print("="*60)
    
    optimizer.close()
    
    print("\n[SUCCESS] Optimization complete!")
    print()

if __name__ == "__main__":
    main()
