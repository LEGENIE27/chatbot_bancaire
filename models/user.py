from datetime import datetime
from models.database import db

class UserModel:
    def __init__(self):
        self.collection = db.get_collection('users')
    
    def create_user(self, user_data):
        """Créer un nouvel utilisateur"""
        user = {
            'customer_id': user_data['customer_id'],
            'email': user_data['email'],
            'phone': user_data.get('phone'),
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'accounts': user_data.get('accounts', []),
            'created_at': datetime.utcnow(),
            'last_login': datetime.utcnow(),
            'status': 'active'
        }
        
        result = self.collection.insert_one(user)
        return result.inserted_id
    
    def find_by_customer_id(self, customer_id):
        """Trouver un utilisateur par son ID client"""
        return self.collection.find_one({'customer_id': customer_id})
    
    def update_last_login(self, customer_id):
        """Mettre à jour la dernière connexion"""
        self.collection.update_one(
            {'customer_id': customer_id},
            {'$set': {'last_login': datetime.utcnow()}}
        )