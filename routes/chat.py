from flask import Blueprint, request, jsonify
from services.nlp_service import NLPService
from services.auth_service import AuthService
from services.fraud_detection import FraudDetectionService
import json
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

nlp_service = NLPService()
auth_service = AuthService()
fraud_detection = FraudDetectionService()

@chat_bp.route('/api/chat/message', methods=['POST'])
def handle_chat_message():
    """Gérer les messages du chat"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data or 'token' not in data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        message = data['message']
        token = data['token']
        
        user_data = auth_service.verify_token(token)
        if not user_data:
            return jsonify({'error': 'Session invalide ou expirée'}), 401
        intent, confidence = nlp_service.detect_intent(message)
        fraud_result = fraud_detection.analyze_message(message, user_data)
        response_data = nlp_service.generate_response(intent, user_data)
        save_chat_history(user_data['user_id'], message, response_data['text'])
        response = {
            'response': response_data['text'],
            'intent': intent,
            'confidence': confidence,
            'fraud_alert': fraud_result['is_suspicious'],
            'risk_level': fraud_result['risk_level']
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Erreur chat: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@chat_bp.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Récupérer l'historique du chat"""
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Token manquant'}), 400
        user_data = auth_service.verify_token(token)
        if not user_data:
            return jsonify({'error': 'Session invalide ou expirée'}), 401
        history = get_user_chat_history(user_data['user_id'])
        
        return jsonify({'history': history})
        
    except Exception as e:
        print(f"Erreur historique: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

def save_chat_history(user_id, user_message, bot_response):
    """Sauvegarder l'historique de conversation"""
    try:
        history_entry = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response
        }
        print(f"Historique sauvegardé pour {user_id}: {user_message}")
        
    except Exception as e:
        print(f"Erreur sauvegarde historique: {e}")

def get_user_chat_history(user_id):
    """Récupérer l'historique de l'utilisateur"""
    try:
        return [] 
    except Exception as e:
        print(f"Erreur récupération historique: {e}")
        return []