import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
from database import TrafficDatabase
import xgboost as xgb
from datetime import datetime, timedelta

def clean_data(df):
    # Remplacer les valeurs infinies par NaN
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Supprimer les lignes avec des valeurs manquantes
    df = df.dropna()
    
    # Traiter les valeurs aberrantes
    for col in df.select_dtypes(include=[np.number]).columns:
        if col != 'value':  # Ne pas traiter la variable cible
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df[col] = df[col].clip(lower_bound, upper_bound)
    
    return df

def create_features(df):
    # Features de base
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['day_of_month'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month
    df['year'] = df['timestamp'].dt.year
    
    # Features supplémentaires
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['quarter'] = df['timestamp'].dt.quarter
    df['is_month_start'] = (df['day_of_month'] == 1).astype(int)
    df['is_month_end'] = (df['day_of_month'] == df['timestamp'].dt.days_in_month).astype(int)
    
    # Moyennes mobiles
    df = df.sort_values('timestamp')
    windows = [3, 6, 12, 24, 48, 72]  # Ajout de fenêtres plus longues
    for window in windows:
        df[f'rolling_{window}h_mean'] = df['value'].rolling(window=window, min_periods=1).mean()
        df[f'rolling_{window}h_std'] = df['value'].rolling(window=window, min_periods=1).std()
        df[f'rolling_{window}h_min'] = df['value'].rolling(window=window, min_periods=1).min()
        df[f'rolling_{window}h_max'] = df['value'].rolling(window=window, min_periods=1).max()
    
    # Lag features
    lags = [1, 2, 3, 4, 5, 6, 12, 24]  # Ajout de plus de lags
    for lag in lags:
        df[f'lag_{lag}'] = df['value'].shift(lag)
    
    # Features temporelles cycliques
    df['hour_sin'] = np.sin(2 * np.pi * df['hour']/24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour']/24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week']/7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week']/7)
    df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
    df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
    
    # Features de tendance
    df['hourly_trend'] = df['value'].pct_change(periods=1)
    df['daily_trend'] = df['value'].pct_change(periods=24)
    
    # Features de saisonnalité
    df['is_peak_hour'] = ((df['hour'] >= 8) & (df['hour'] <= 20)).astype(int)
    df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)
    
    return df

def evaluate_model():
    # Initialiser la base de données
    db = TrafficDatabase()
    
    # Récupérer toutes les données
    df = db.get_all_traffic_data()
    
    if len(df) < 100:
        print("Attention: Le nombre de données est faible pour une évaluation fiable.")
        print(f"Nombre de données disponibles: {len(df)}")
        return
    
    # Préparer les données
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = create_features(df)
    df = clean_data(df)  # Nettoyer les données
    
    # Sélectionner toutes les features numériques sauf la target
    feature_columns = [col for col in df.columns if col not in ['timestamp', 'value']]
    
    X = df[feature_columns]
    y = df['value']
    
    # Diviser les données
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    
    # Normaliser les données
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Créer les ensembles de données DMatrix pour XGBoost
    dtrain = xgb.DMatrix(X_train_scaled, label=y_train)
    dtest = xgb.DMatrix(X_test_scaled, label=y_test)
    
    # Paramètres optimisés du modèle
    params = {
        'objective': 'reg:squarederror',
        'learning_rate': 0.05,  # Réduit pour plus de stabilité
        'max_depth': 8,         # Augmenté pour capturer plus de complexité
        'min_child_weight': 2,  # Augmenté pour réduire le surapprentissage
        'subsample': 0.9,       # Augmenté pour plus de stabilité
        'colsample_bytree': 0.9,
        'gamma': 0.1,          # Ajouté pour contrôler la complexité
        'reg_alpha': 0.1,      # Ajouté pour la régularisation L1
        'reg_lambda': 1,       # Ajouté pour la régularisation L2
        'random_state': 42
    }
    
    # Entraîner le modèle avec plus d'itérations
    model = xgb.train(
        params,
        dtrain,
        num_boost_round=500,  # Augmenté pour permettre plus d'apprentissage
        evals=[(dtest, 'test')],
        early_stopping_rounds=20,  # Augmenté pour plus de patience
        verbose_eval=False
    )
    
    # Faire des prédictions
    y_pred = model.predict(dtest)
    
    # Calculer les métriques
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred) * 100
    r2 = r2_score(y_test, y_pred)
    
    # Afficher les résultats
    print("\n=== Évaluation du modèle de prédiction de trafic ===")
    print(f"Nombre total de données: {len(df)}")
    print(f"Taille de l'ensemble d'entraînement: {len(X_train)}")
    print(f"Taille de l'ensemble de test: {len(X_test)}")
    print(f"Nombre de features utilisées: {len(feature_columns)}")
    print("\nMétriques de performance:")
    print(f"Mean Squared Error (MSE): {mse:.2f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")
    print(f"R² Score: {r2:.4f}")
    
    # Afficher l'importance des features
    print("\nTop 10 des features les plus importantes:")
    importance = model.get_score(importance_type='gain')
    feature_importance = pd.DataFrame({
        'Feature': list(importance.keys()),
        'Importance': list(importance.values())
    }).sort_values('Importance', ascending=False).head(10)
    print(feature_importance)

if __name__ == "__main__":
    evaluate_model() 