"""
Train ML model for delay prediction
"""
import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error
import joblib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'marocrail.db')
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')

def load_training_data():
    """Load and join data from database"""
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        d.delay_id,
        d.delay_minutes,
        d.delay_reason,
        d.weather_condition,
        strftime('%H', d.timestamp) as hour,
        strftime('%w', d.timestamp) as day_of_week,
        strftime('%m', d.timestamp) as month,
        s.departure_time,
        s.platform,
        t.train_type,
        t.capacity,
        r.distance_km,
        r.typical_duration_minutes,
        r.origin_station_id,
        r.destination_station_id
    FROM delays d
    JOIN schedules s ON d.schedule_id = s.schedule_id
    JOIN trains t ON s.train_id = t.train_id
    JOIN routes r ON s.route_id = r.route_id
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"[OK] Loaded {len(df)} delay records for training")
    return df

def calculate_route_delay_stats(df):
    """Calculate historical delay stats per route"""
    route_stats = df.groupby(['origin_station_id', 'destination_station_id']).agg({
        'delay_minutes': ['mean', 'std', 'count']
    }).reset_index()
    
    route_stats.columns = ['origin_station_id', 'destination_station_id', 
                           'route_avg_delay', 'route_std_delay', 'route_delay_count']
    
    return route_stats

def engineer_features(df):
    """Create ML features"""
    df = df.copy()
    
    # Time features
    df['hour'] = df['hour'].astype(int)
    df['day_of_week'] = df['day_of_week'].astype(int)
    df['month'] = df['month'].astype(int)
    df['is_peak_hour'] = ((df['hour'] >= 6) & (df['hour'] <= 9)) | ((df['hour'] >= 17) & (df['hour'] <= 20))
    df['is_weekend'] = df['day_of_week'].isin([0, 6])  # Sunday=0, Saturday=6
    
    # Weather binary flags
    for weather in ['cloudy', 'foggy', 'hot', 'rainy', 'sunny']:
        df[f'weather_{weather}'] = (df['weather_condition'] == weather).astype(int)
    
    # Train type encoding
    train_type_map = {'Al Boraq': 3, 'TNR': 2, 'Regular': 1}
    df['train_type_code'] = df['train_type'].map(train_type_map)
    
    # Route stats
    route_stats = calculate_route_delay_stats(df)
    df = df.merge(route_stats, on=['origin_station_id', 'destination_station_id'], how='left')
    df['route_avg_delay'] = df['route_avg_delay'].fillna(df['delay_minutes'].mean())
    df['route_std_delay'] = df['route_std_delay'].fillna(0)
    
    # Season
    df['season'] = df['month'].apply(lambda m: 
        'winter' if m in [12, 1, 2] else
        'spring' if m in [3, 4, 5] else
        'summer' if m in [6, 7, 8] else 'autumn'
    )
    for season in ['autumn', 'spring', 'summer', 'winter']:
        df[f'season_{season}'] = (df['season'] == season).astype(int)
    
    return df

def prepare_classification_data(df):
    """Prepare data for delay classification (will it delay?)"""
    feature_cols = [
        'hour', 'day_of_week', 'month', 'is_peak_hour', 'is_weekend',
        'weather_cloudy', 'weather_foggy', 'weather_hot', 'weather_rainy', 'weather_sunny',
        'train_type_code', 'capacity', 'distance_km', 'typical_duration_minutes',
        'route_avg_delay', 'route_std_delay',
        'season_autumn', 'season_spring', 'season_summer', 'season_winter'
    ]
    
    X = df[feature_cols].fillna(0)
    y = (df['delay_minutes'] > 5).astype(int)  # Delay if >5 minutes
    
    return X, y, feature_cols

def prepare_regression_data(df):
    """Prepare data for delay duration prediction"""
    delayed_df = df[df['delay_minutes'] > 5].copy()
    
    feature_cols = [
        'hour', 'day_of_week', 'month', 'is_peak_hour', 'is_weekend',
        'weather_cloudy', 'weather_foggy', 'weather_hot', 'weather_rainy', 'weather_sunny',
        'train_type_code', 'capacity', 'distance_km', 'typical_duration_minutes',
        'route_avg_delay', 'route_std_delay',
        'season_autumn', 'season_spring', 'season_summer', 'season_winter'
    ]
    
    X = delayed_df[feature_cols].fillna(0)
    y = delayed_df['delay_minutes']
    
    return X, y, feature_cols

def train_classifier(X, y):
    """Train Random Forest classifier"""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1
    )
    
    print("\n[INFO] Training classifier...")
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"[OK] Classifier trained - Accuracy: {accuracy:.2%}")
    
    return clf, X_test, y_test, y_pred

def train_regressor(X, y):
    """Train Random Forest regressor"""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    reg = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1
    )
    
    print("\n[INFO] Training regressor...")
    reg.fit(X_train, y_train)
    
    y_pred = reg.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"[OK] Regressor trained - MAE: {mae:.2f} minutes")
    
    return reg, X_test, y_test, y_pred

def evaluate_model(clf, X_test, y_test, y_pred):
    """Print detailed evaluation"""
    print("\n" + "="*60)
    print("  Classification Report")
    print("="*60)
    print(classification_report(y_test, y_pred, target_names=['No Delay', 'Delayed']))

def feature_importance(model, feature_names):
    """Show top important features"""
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n" + "="*60)
    print("  Top 10 Important Features")
    print("="*60)
    for idx, row in importance.head(10).iterrows():
        print(f"  {row['feature']:30s} {row['importance']:.4f}")

def save_models(clf, reg, feature_cols):
    """Save trained models"""
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    joblib.dump(clf, os.path.join(MODEL_DIR, 'delay_classifier.pkl'))
    joblib.dump(reg, os.path.join(MODEL_DIR, 'delay_regressor.pkl'))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, 'feature_columns.pkl'))
    
    print(f"\n[OK] Models saved to {MODEL_DIR}")

def main():
    print("="*60)
    print("  MarocRail-Optimizer - ML Model Training")
    print("="*60)
    
    df = load_training_data()
    
    print("\n[INFO] Engineering features...")
    df = engineer_features(df)
    print(f"[OK] Created {len(df.columns)} features")
    
    # Classification model
    print("\n[STEP 1/2] Training delay classifier...")
    X_clf, y_clf, feature_cols = prepare_classification_data(df)
    clf, X_test_clf, y_test_clf, y_pred_clf = train_classifier(X_clf, y_clf)
    evaluate_model(clf, X_test_clf, y_test_clf, y_pred_clf)
    feature_importance(clf, feature_cols)
    
    # Regression model
    print("\n[STEP 2/2] Training delay duration predictor...")
    X_reg, y_reg, _ = prepare_regression_data(df)
    reg, X_test_reg, y_test_reg, y_pred_reg = train_regressor(X_reg, y_reg)
    
    save_models(clf, reg, feature_cols)
    
    print("\n" + "="*60)
    print("  [SUCCESS] Model training complete!")
    print("="*60)
    print()

if __name__ == "__main__":
    main()
