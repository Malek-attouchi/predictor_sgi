import joblib
from predict_traffic import train_model
from database import TrafficDatabase
import os

def save_model():
    # Charger les données depuis la base PostgreSQL
    db = TrafficDatabase()
    df = db.get_all_traffic_data()
    if df.empty:
        print("Aucune donnée trouvée dans la base de données !")
        return
    # Entraîner le modèle
    model, scaler = train_model(df)
    # Créer le dossier models si besoin
    if not os.path.exists('models'):
        os.makedirs('models')
    # Sauvegarder le modèle et le scaler
    joblib.dump(model, 'models/traffic_model.joblib')
    joblib.dump(scaler, 'models/traffic_scaler.joblib')
    print("Model and scaler saved successfully with PostgreSQL data!")

if __name__ == "__main__":
    save_model() 