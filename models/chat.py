from datetime import datetime
from models.database import db

class ChatModel:
    def __init__(self):
        self.sessions = db.get_collection('chat_sessions')
        self.messages = db.get_collection('chat_messages')
        self.fraud_alerts = db.get_collection('fraud_alerts')
    
    def create_session(self, user_id):
        """Créer une nouvelle session de chat"""
        session = {
            'user_id': user_id,
            'session_token': f"session_{datetime.utcnow().timestamp()}",
            'start_time': datetime.utcnow(),
            'end_time': None,
            'status': 'active',
            'satisfaction_score': None
        }
        
        result = self.sessions.insert_one(session)
        return result.inserted_id, session['session_token']
    
    def add_message(self, session_id, message_data):
        """Ajouter un message à la conversation"""
        message = {
            'session_id': session_id,
            'message_text': message_data['text'],
            'is_user_message': message_data['is_user_message'],
            'intent_detected': message_data.get('intent'),
            'confidence_score': message_data.get('confidence'),
            'timestamp': datetime.utcnow(),
            'fraud_alert_triggered': message_data.get('fraud_alert', False)
        }
        
        result = self.messages.insert_one(message)
        return result.inserted_id
    
    def create_fraud_alert(self, alert_data):
        """Créer une alerte de fraude"""
        alert = {
            'user_id': alert_data['user_id'],
            'session_id': alert_data.get('session_id'),
            'message_id': alert_data.get('message_id'),
            'alert_type': alert_data['alert_type'],
            'confidence_score': alert_data['confidence_score'],
            'description': alert_data['description'],
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'resolved_at': None
        }
        
        result = self.fraud_alerts.insert_one(alert)
        return result.inserted_id