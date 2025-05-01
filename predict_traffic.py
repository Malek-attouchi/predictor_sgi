import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from datetime import datetime
from database import TrafficDatabase
import pickle
import os

def load_or_train_model():
    """Charge le modèle existant ou en entraîne un nouveau si nécessaire"""
    model_path = 'models/traffic_model.pkl'
    scaler_path = 'models/scaler.pkl'
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        # Charger le modèle et le scaler existants
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
    else:
        # Créer le dossier models s'il n'existe pas
        os.makedirs('models', exist_ok=True)
        
        # Entraîner un nouveau modèle
        db = TrafficDatabase()
        df = db.get_all_traffic_data()
        df = prepare_data(df)
        
        X = df.drop(['timestamp', 'value'], axis=1)
        y = df['value']
        
        # Normaliser les données
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Entraîner le modèle
        dtrain = xgb.DMatrix(X_scaled, label=y)
        params = {
            'objective': 'reg:squarederror',
            'learning_rate': 0.05,
            'max_depth': 8,
            'min_child_weight': 2,
            'subsample': 0.9,
            'colsample_bytree': 0.9,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1,
            'random_state': 42
        }
        model = xgb.train(params, dtrain, num_boost_round=500)
        
        # Sauvegarder le modèle et le scaler
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
    
    return model, scaler

def prepare_data(df):
    """Prépare les données pour la prédiction"""
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Features temporelles
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['day_of_month'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month
    df['year'] = df['timestamp'].dt.year
    df['quarter'] = df['timestamp'].dt.quarter
    
    # Features supplémentaires
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_month_start'] = (df['day_of_month'] == 1).astype(int)
    df['is_month_end'] = (df['day_of_month'] == df['timestamp'].dt.days_in_month).astype(int)
    df['is_peak_hour'] = ((df['hour'] >= 8) & (df['hour'] <= 20)).astype(int)
    df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)
    
    # Features cycliques
    df['hour_sin'] = np.sin(2 * np.pi * df['hour']/24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour']/24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week']/7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week']/7)
    df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
    df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
    
    return df

def predict_traffic(date_str):
    """
    Prédit le trafic pour une date donnée
    
    Args:
        date_str (str): Date au format 'DD/MM/YYYY HH:mm' ou 'YYYY-MM-DD HH:mm'
    
    Returns:
        dict: Dictionnaire contenant la prédiction et les informations associées
    """
    try:
        # Essayer différents formats de date
        try:
            date = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
        except ValueError:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            except ValueError:
                raise ValueError("Format de date invalide. Utilisez 'DD/MM/YYYY HH:mm' ou 'YYYY-MM-DD HH:mm'")
        
        # Créer un DataFrame avec la date
        df = pd.DataFrame({'timestamp': [date]})
        df = prepare_data(df)
        
        # Charger le modèle et le scaler
        model, scaler = load_or_train_model()
        
        # Préparer les features pour la prédiction
        X = df.drop('timestamp', axis=1)
        X_scaled = scaler.transform(X)
        
        # Faire la prédiction
        dtest = xgb.DMatrix(X_scaled)
        prediction = model.predict(dtest)[0]
        
        # Formater la sortie
        result = {
            'date': date.strftime('%d/%m/%Y %H:%M'),
            'prediction': prediction,
            'prediction_formatted': format_traffic(prediction),
            'features': {
                'heure': date.hour,
                'jour_semaine': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][date.weekday()],
                'weekend': 'Oui' if df['is_weekend'].iloc[0] else 'Non',
                'heure_de_pointe': 'Oui' if df['is_peak_hour'].iloc[0] else 'Non'
            }
        }
        
        return result
        
    except Exception as e:
        return {'error': str(e)}

def format_traffic(value):
    """Formate la valeur du trafic en b/s, kb/s ou Mb/s"""
    if value < 1000:
        return f"{value:.2f} b/s"
    elif value < 1000000:
        return f"{value/1000:.2f} kb/s"
    else:
        return f"{value/1000000:.2f} Mb/s"

if __name__ == "__main__":
    # Exemple d'utilisation
    date_test = "17/03/2024 14:30"
    result = predict_traffic(date_test)
    
    if 'error' in result:
        print(f"Erreur: {result['error']}")
    else:
        print("\n=== Prédiction de trafic ===")
        print(f"Date: {result['date']}")
        print(f"Trafic prédit: {result['prediction_formatted']}")
        print("\nInformations complémentaires:")
        for key, value in result['features'].items():
            print(f"{key.replace('_', ' ').title()}: {value}")