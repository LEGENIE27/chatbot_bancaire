# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/banque_db')
    DATABASE_NAME = 'banque_db'
    SECRET_KEY = os.getenv('SECRET_KEY', 'votre_cle_secrete_super_securisee_ici')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
    NLP_MODEL = 'fr_core_news_sm'
    SESSION_TIMEOUT = 3600