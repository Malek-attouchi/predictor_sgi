from sqlalchemy import Column, Integer, Float, DateTime, String, create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd
from db_config import DATABASE_URL, Base, engine
import logging
from pandas import Timestamp
from sqlalchemy.ext.declarative import declarative_base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrafficData(Base):
    __tablename__ = 'traffic_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    source = Column(String)

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    predicted_value = Column(Float, nullable=False)
    actual_value = Column(Float)

class TrafficDatabase:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.create_tables()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def _convert_to_datetime(self, timestamp):
        try:
            if isinstance(timestamp, Timestamp):
                return timestamp.to_pydatetime()
            elif isinstance(timestamp, datetime):
                return timestamp
            elif isinstance(timestamp, str):
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%d/%m/%Y %H:%M:%S',
                    '%d/%m/%Y %H:%M',
                    '%Y-%m-%d',
                    '%d/%m/%Y',
                    '%H:%M:%S',
                    '%H:%M'
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(timestamp, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Format de date non reconnu: {timestamp}")
            else:
                raise ValueError(f"Type de timestamp non supporté: {type(timestamp)}")
        except Exception as e:
            logger.error(f"Erreur lors de la conversion du timestamp: {str(e)}")
            raise

    def add_traffic_data(self, df, source=None):
        session = self.SessionLocal()
        try:
            for _, row in df.iterrows():
                timestamp = self._convert_to_datetime(row['timestamp'])
                traffic_data = TrafficData(
                    timestamp=timestamp,
                    value=float(row['value']),
                    source=source
                )
                session.add(traffic_data)
            session.commit()
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des données: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    def get_all_traffic_data(self):
        session = self.SessionLocal()
        try:
            result = session.query(TrafficData).order_by(TrafficData.timestamp).all()
            df = pd.DataFrame([(r.timestamp, r.value) for r in result],
                            columns=['timestamp', 'value'])
            return df
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {str(e)}")
            raise
        finally:
            session.close()

    def add_prediction(self, timestamp, predicted_value):
        session = self.SessionLocal()
        try:
            timestamp = self._convert_to_datetime(timestamp)
            prediction = Prediction(
                timestamp=timestamp,
                predicted_value=predicted_value
            )
            session.add(prediction)
            session.commit()
            return prediction.id
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la prédiction: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    def get_recent_predictions(self, limit=10):
        session = self.SessionLocal()
        try:
            predictions = session.query(Prediction)\
                .order_by(Prediction.timestamp.desc())\
                .limit(limit)\
                .all()
            return predictions
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des prédictions: {str(e)}")
            raise
        finally:
            session.close()

    def update_prediction_with_actual(self, prediction_id, actual_value):
        session = self.SessionLocal()
        try:
            prediction = session.query(Prediction).get(prediction_id)
            if prediction:
                prediction.actual_value = actual_value
                session.commit()
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la prédiction: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    def get_model_performance(self):
        session = self.SessionLocal()
        try:
            predictions = session.query(Prediction)\
                .filter(Prediction.actual_value.isnot(None))\
                .all()
            
            if not predictions:
                return pd.DataFrame({'mae': [0], 'mape': [0]})
            
            actual_values = [p.actual_value for p in predictions]
            predicted_values = [p.predicted_value for p in predictions]
            
            mae = sum(abs(a - p) for a, p in zip(actual_values, predicted_values)) / len(predictions)
            mape = sum(abs((a - p) / a) * 100 for a, p in zip(actual_values, predicted_values)) / len(predictions)
            
            return pd.DataFrame({'mae': [mae], 'mape': [mape]})
        except Exception as e:
            logger.error(f"Erreur lors du calcul des performances: {str(e)}")
            raise
        finally:
            session.close()