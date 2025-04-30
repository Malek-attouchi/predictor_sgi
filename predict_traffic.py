import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime

def convert_to_bits(value):
    if isinstance(value, str):
        if 'kb/s' in value:
            return float(value.replace('kb/s', '').strip()) * 1000
        elif 'mb/s' in value:
            return float(value.replace('Mb/s', '').strip()) * 1000000
        elif 'b/s' in value:
            return float(value.replace('b/s', '').strip())
    return float(value)

def load_data(file_path=None):
    if file_path:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['value'] = df['value'].apply(convert_to_bits)
    else:
        data = """2025-02-17 12:00:00,695 b/s
2025-02-17 13:00:00,589 b/s
2025-02-17 14:00:00,2.64 kb/s
2025-02-17 15:00:00,697 b/s
2025-02-17 16:00:00,599 b/s
2025-02-17 17:00:00,682 b/s
2025-02-17 18:00:00,550 b/s
2025-02-17 19:00:00,549 b/s
2025-02-17 20:00:00,548 b/s
2025-02-17 21:00:00,550 b/s
2025-02-17 22:00:00,544 b/s
2025-02-17 23:00:00,569 b/s
2025-02-18 00:00:00,541 b/s
2025-02-18 01:00:00,542 b/s
2025-02-18 02:00:00,544 b/s
2025-02-18 03:00:00,537 b/s
2025-02-18 04:00:00,541 b/s
2025-02-18 05:00:00,551 b/s
2025-02-18 06:00:00,541 b/s
2025-02-18 07:00:00,544 b/s
2025-02-18 08:00:00,543 b/s
2025-02-18 09:00:00,559 b/s
2025-02-18 10:00:00,24.6 kb/s
2025-02-18 11:00:00,558 b/s
2025-02-18 12:00:00,556 b/s
2025-02-18 13:00:00,574 b/s
2025-02-18 14:00:00,535 b/s
2025-02-18 15:00:00,44.5 kb/s
2025-02-18 16:00:00,5.63 kb/s
2025-02-18 17:00:00,3.00 kb/s
2025-02-18 18:00:00,1.16 kb/s
2025-02-18 19:00:00,1.34 kb/s
2025-02-18 20:00:00,1.86 kb/s
2025-02-18 21:00:00,939 b/s
2025-02-18 22:00:00,14.2 kb/s
2025-02-18 23:00:00,1.23 kb/s
2025-02-19 00:00:00,1.18 kb/s
2025-02-19 01:00:00,4.99 kb/s
2025-02-19 02:00:00,735 b/s
2025-02-19 03:00:00,1.09 kb/s
2025-02-19 04:00:00,6.41 kb/s
2025-02-19 05:00:00,2.76 kb/s
2025-02-19 06:00:00,1.65 kb/s
2025-02-19 07:00:00,1.40 kb/s
2025-02-19 08:00:00,1.48 kb/s
2025-02-19 09:00:00,1.88 kb/s
2025-02-19 10:00:00,2.40 kb/s
2025-02-19 11:00:00,11.9 kb/s
2025-02-19 12:00:00,1.81 kb/s
2025-02-19 13:00:00,3.02 kb/s
2025-02-19 14:00:00,859 b/s
2025-02-19 15:00:00,1.08 kb/s
2025-02-19 16:00:00,1.18 kb/s
2025-02-19 17:00:00,2.11 kb/s
2025-02-19 18:00:00,973 b/s
2025-02-19 19:00:00,1.63 kb/s
2025-02-19 20:00:00,668 b/s
2025-02-19 21:00:00,589 b/s
2025-02-19 22:00:00,1.13 kb/s
2025-02-19 23:00:00,2.43 kb/s
2025-02-20 00:00:00,16.5 kb/s"""
        lines = [line.strip() for line in data.split('\n')]
        df = pd.DataFrame([line.split(',') for line in lines], columns=['timestamp', 'value'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['value'] = df['value'].apply(convert_to_bits)
    return df

def train_model(df):
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['day_of_month'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month

    X = df[['hour', 'day_of_week', 'day_of_month', 'month']]
    y = df['value']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

    return model, scaler

def predict_traffic(model, scaler, date_str):
    try:
        date = datetime.strptime(date_str, '%d/%m/%Y')
        features = np.array([[
            date.hour,
            date.weekday(),
            date.day,
            date.month
        ]])
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        return prediction
    except ValueError:
        return None