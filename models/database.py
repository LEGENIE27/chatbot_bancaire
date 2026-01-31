from pymongo import MongoClient
from config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Établir la connexion à MongoDB en local"""
        try:
            self.client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[config.DATABASE_NAME]
            logger.info(" Connecté à MongoDB Local avec succès!")
            logger.info(f" Base de données: {config.DATABASE_NAME}")
        except Exception as e:
            logger.error(f" Erreur de connexion MongoDB: {e}")
            logger.info(" Vérifiez que MongoDB est démarré: mongod --dbpath /chemin/vers/data/db")
            raise e
    
    def get_collection(self, collection_name):
        """Récupérer une collection"""
        if self.db is None:
            self.connect()
        return self.db[collection_name]
    
    def create_indexes(self):
        """Créer les index pour optimiser les performances"""
        try:
            self.db.users.create_index("customer_id", unique=True)
            self.db.users.create_index("email")
            self.db.chat_sessions.create_index("session_token")
            self.db.chat_sessions.create_index("user_id")
            self.db.chat_sessions.create_index("start_time")
            self.db.chat_messages.create_index("session_id")
            self.db.chat_messages.create_index("timestamp")
            self.db.fraud_alerts.create_index("user_id")
            self.db.fraud_alerts.create_index("status")
            self.db.fraud_alerts.create_index("created_at")      
            logger.info("Index MongoDB créés avec succès!")   
        except Exception as e:
            logger.warning(f"Erreur lors de la création des index: {e}")
    
    def close_connection(self):
        """Fermer la connexion"""
        if self.client:
            self.client.close()
            logger.info("🔌 Connexion MongoDB fermée")
db = MongoDB()