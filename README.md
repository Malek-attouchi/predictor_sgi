# Traffic Predictor

Une application de prédiction de trafic réseau utilisant l'apprentissage automatique pour prévoir le trafic à différentes échelles de temps.

## Fonctionnalités

- **Prédiction unique** : Prédit le trafic pour un moment spécifique
- **Prédiction journalière** : Affiche les prédictions pour une journée entière
- **Visualisation des données** : Graphiques et tableaux pour une meilleure compréhension
- **Interface utilisateur moderne** : Design responsive avec Material-UI
- **Stockage des données** : Utilisation de PostgreSQL pour la persistance des données

## Architecture

Le projet est divisé en deux parties principales :

### Backend (FastAPI)
- API RESTful pour les prédictions
- Gestion de la base de données PostgreSQL
- Modèle d'apprentissage automatique pour les prédictions
- Endpoints :
  - `/predict` : Prédiction unique
  - `/predict_day` : Prédiction journalière
  - `/traffic_data` : Récupération des données historiques

### Frontend (React + TypeScript)
- Interface utilisateur moderne avec Material-UI
- Visualisation des données avec Chart.js
- Gestion d'état avec React Hooks
- Design responsive

## Prérequis

- Python 3.8+
- Node.js 16+
- PostgreSQL
- pip (gestionnaire de paquets Python)
- npm (gestionnaire de paquets Node.js)

## Installation

### Backend

1. Créez un environnement virtuel Python :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

2. Installez les dépendances Python :
```bash
pip install -r requirements.txt
```

3. Configurez la base de données PostgreSQL :
- Créez une base de données nommée `traffic_db`
- Mettez à jour les informations de connexion dans `database.py`

4. Lancez le serveur FastAPI :
```bash
uvicorn server:app --reload
```

### Frontend

1. Installez les dépendances Node.js :
```bash
cd frontend
npm install
```

2. Lancez le serveur de développement :
```bash
npm run dev
```

## Utilisation

1. Accédez à l'application via `http://localhost:5173`
2. Sélectionnez le type de prédiction (unique ou journalière)
3. Choisissez une date et une heure
4. Cliquez sur "Lancer la prédiction"
5. Visualisez les résultats sous forme de graphique ou de tableau

## Structure du Projet

```
traffic-predictor/
├── frontend/                 # Application React
│   ├── src/
│   │   ├── App.tsx          # Composant principal
│   │   └── ...              # Autres composants
│   ├── package.json         # Dépendances frontend
│   └── vite.config.ts       # Configuration Vite
├── models/                  # Modèles sauvegardés
│   ├── traffic_model.joblib
│   └── traffic_scaler.joblib
├── database.py             # Configuration de la base de données
├── server.py              # API FastAPI
├── save_model.py          # Script de sauvegarde du modèle
└── requirements.txt       # Dépendances Python
```

## Technologies Utilisées

### Backend
- FastAPI
- scikit-learn
- SQLAlchemy
- PostgreSQL
- joblib

### Frontend
- React
- TypeScript
- Material-UI
- Chart.js
- Vite

## Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur GitHub. 