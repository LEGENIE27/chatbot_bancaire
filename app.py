from flask import Flask, request, jsonify, render_template, session, redirect
from pymongo import MongoClient
import spacy
from datetime import datetime, timedelta
import logging
import secrets
import hashlib
from config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

try:
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.DATABASE_NAME]  
    users_collection = db.users  
    conversations_collection = db.conversations
    logger.info(" Connexion MongoDB établie")
except Exception as e:
    logger.error(f" Erreur MongoDB: {e}")
    client = None
    db = None
    users_collection = None
    conversations_collection = None

try:
    nlp = spacy.load(Config.NLP_MODEL)
    logger.info("Modèle NLP chargé")
except Exception as e:
    logger.warning(f"  Modèle NLP non chargé: {e}")
    nlp = None

active_sessions = {}

def format_currency(amount, currency='XOF'):
    """Formater un montant avec la devise appropriée"""
    if currency == 'XOF' or currency == 'FCFA':
        return f"{amount:,.0f} FCFA"
    elif currency == 'EUR':
        return f"{amount:,.2f} €"
    else:
        return f"{amount:,.2f} {currency}"

@app.route('/')
def home():
    return jsonify({
        "status": "Server is running",
        "message": "Bank Chatbot API",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "database": "connected" if client else "disconnected",
        "nlp_model": "loaded" if nlp else "failed"
    })

@app.route('/login')
def login_page():
    """Page de connexion"""
    return render_template('login.html')

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authentification par email"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email et mot de passe requis"}), 400
        user_data = users_collection.find_one({"email": email})
        if not user_data:
            return jsonify({"error": "Email ou mot de passe incorrect"}), 401
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user_data.get('password') != password_hash:
            return jsonify({"error": "Email ou mot de passe incorrect"}), 401
        session_token = secrets.token_urlsafe(32)
        session_id = f"session_{user_data['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        active_sessions[session_token] = {
            'user_id': user_data['user_id'],
            'session_id': session_id,
            'user_data': {
                'name': user_data['name'],
                'email': user_data['email'],
                'balance': user_data['balance'],
                'card_status': user_data['card_status'],
                'phone': user_data.get('phone', ''),
                'transactions': user_data.get('transactions', [])
            },
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        
        logger.info(f" Connexion réussie pour {email}")
        
        return jsonify({
            "session_token": session_token,
            "session_id": session_id,
            "user_name": user_data['name'],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erreur login: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Données JSON requises"}), 400
            
        user_message = data.get('message', '')
        session_token = data.get('token', '')
        
        if not user_message:
            return jsonify({"error": "Message requis"}), 400
        
        if not session_token:
            return jsonify({"error": "Token de session requis"}), 401
    
        session_data = active_sessions.get(session_token)
        if not session_data:
            return jsonify({"error": "Session invalide ou expirée"}), 401
        
        user_id = session_data['user_id']
        session_id = session_data['session_id']
        user_data = session_data['user_data']
        
        logger.info(f" Message de {user_data['name']}: {user_message}")
        
        active_sessions[session_token]['last_activity'] = datetime.now()
        response = process_message(user_message, user_data)
        fraud_alert = False
        risk_level = None
        if any(word in user_message.lower() for word in ['fraude', 'frauduleuse', 'vol', 'pirate', 'hack']):
            fraud_alert = True
            risk_level = 'medium'
            response = " Alerte de sécurité ! Nous avons détecté une mention de fraude. Veuillez immédiatement contacter notre service sécurité au 0 800 123 456."
        if 'bloquer' in user_message.lower() and any(word in user_message.lower() for word in ['carte', 'cb']):
            if user_data['card_status'] == 'active':
    
                users_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"card_status": "blocked"}}
                )
                
                active_sessions[session_token]['user_data']['card_status'] = 'blocked'
        save_conversation(user_id, user_message, response, session_id, fraud_alert)
        
        return jsonify({
            "response": response,
            "fraud_alert": fraud_alert,
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erreur chat message: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    try:
        session_token = request.args.get('token', '')
        
        if not session_token:
            return jsonify({"error": "Token de session requis"}), 401
        
        session_data = active_sessions.get(session_token)
        if not session_data:
            return jsonify({"error": "Session invalide ou expirée"}), 401
        
        user_id = session_data['user_id']
    
        history = []
        if conversations_collection:
            conversations = conversations_collection.find(
                {"user_id": user_id}
            ).sort("timestamp", 1).limit(20)
            
            for conv in conversations:
                history.append({
                    "text": conv.get('user_message', ''),
                    "is_user": True
                })
                history.append({
                    "text": conv.get('bot_response', ''),
                    "is_user": False
                })
        
        return jsonify({"history": history})
            
    except Exception as e:
        logger.error(f"Erreur récupération historique: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

@app.route('/chat-ui')
def chat_ui():
    """Serve l'interface de chat (protégée)"""
    token = request.args.get('token')
    
    if not token or token not in active_sessions:
        return redirect('/login')
    
    return render_template('chat.html')

def process_message(message, user_data=None):
    """Fonction améliorée de traitement des messages avec vraies données utilisateur - FORMAT CFA"""
    message_lower = message.lower().strip()
    
    if any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'coucou', 'hey']):
        if user_data:
            return f"Bonjour {user_data['name'].split()[0]} !  Comment puis-je vous aider aujourd'hui ?"
        else:
            return "Bonjour !  Comment puis-je vous aider aujourd'hui ?"
    
    elif any(word in message_lower for word in ['solde', 'compte', 'argent', 'montant']):
        if user_data:
            formatted_balance = format_currency(user_data['balance'], 'XOF')
            return f" Votre solde actuel est de **{formatted_balance}**. Cette information est mise à jour quotidiennement."
        else:
            return "Je ne peux pas accéder à vos informations de solde. Veuillez vous reconnecter."
    elif 'bloquer' in message_lower and any(word in message_lower for word in ['carte', 'cb', 'bancaire']):
        if user_data:
            if user_data['card_status'] == 'active':
                return " Votre carte a été **bloquée avec succès** ! Une nouvelle carte vous sera envoyée sous 3-5 jours ouvrés. Souhaitez-vous un retrait d'urgence en agence ?"
            else:
                return "Votre carte est déjà bloquée. Une nouvelle carte a déjà été commandée."
        else:
            return "Je ne peux pas effectuer cette opération. Veuillez vous reconnecter."
    elif any(word in message_lower for word in ['carte', 'cb', 'bancaire', 'mastercard', 'visa']):
        if user_data:
            status = "🟢 Active" if user_data['card_status'] == 'active' else "🔴 Bloquée"
            return f"💳 Statut de votre carte : {status}\nJe peux vous aider avec :\n• Bloquer une carte\n• Signaler une perte/vol\n• Modifier vos plafonds"
        else:
            return "💳 Je peux vous aider avec la gestion de votre carte bancaire."

    elif any(word in message_lower for word in ['transaction', 'historique', 'opération', 'dépense']):
        if user_data and user_data.get('transactions'):
            transactions_text = "📊 Voici vos 5 dernières transactions :\n"
            for tx in user_data['transactions'][:5]:
                emoji = "🟢" if tx['amount'] > 0 else "🔴"
                formatted_amount = format_currency(tx['amount'], 'XOF')
                transactions_text += f"• {emoji} {tx['date']} - {tx['description']} - {formatted_amount}\n"
            return transactions_text
        else:
            return "Vous pouvez consulter vos 30 derniers jours de transactions dans votre espace client."*
    elif any(word in message_lower for word in ['virement', 'transfert', 'envoyer argent']):
        return " Pour effectuer un virement, veuillez vous connecter à votre espace client sécurisé. Je peux vous guider dans les étapes si besoin !"
    
    elif any(word in message_lower for word in ['qui es-tu', 'qui est tu', 'présente', 'tu es qui', 'ton nom']):
        return " Je suis l'assistant virtuel de votre banque ! Je peux vous aider avec vos questions sur les comptes, cartes, transactions et services bancaires."
    
    elif any(word in message_lower for word in ['merci', 'thanks', 'parfait', 'super']):
        return "Je vous en prie !  N'hésitez pas si vous avez d'autres questions."
    
    elif any(word in message_lower for word in ['bye', 'au revoir', 'à plus', 'salut']):
        return "Au revoir ! Passez une excellente journée !"
  
    elif any(word in message_lower for word in ['fraude', 'vol', 'pirate', 'hack', 'urgence']):
        return "🚨 **ALERTE SÉCURITÉ** 🚨\nVeuillez immédiatement contacter notre service sécurité au **0 800 123 456** (24h/24)."
    
    else:
        return "Je comprends que vous avez une question.  Pour une assistance personnalisée, nos conseillers sont disponibles au **0 800 123 456** de 8h à 20h."

def save_conversation(user_id, user_message, bot_response, session_id="default", fraud_alert=False):
    """Sauvegarde la conversation en base de données"""
    try:
        if conversations_collection is None:
            logger.warning("Collection conversations non disponible")
            return
            
        conversation = {
            "user_id": user_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "session_id": session_id,
            "fraud_alert": fraud_alert,
            "timestamp": datetime.now()
        }
        conversations_collection.insert_one(conversation)
        logger.info(f" Conversation sauvegardée pour {user_id}")
    except Exception as e:
        logger.error(f"Erreur sauvegarde conversation: {e}")

@app.route('/conversations/<user_id>', methods=['GET'])
def get_conversations(user_id):
    """Récupère l'historique des conversations d'un utilisateur"""
    try:
        if conversations_collection is None:
            return jsonify({"error": "Base de données non disponible"}), 500
            
        conversations = conversations_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(10)
        
        result = []
        for conv in conversations:
            result.append({
                "user_message": conv.get("user_message", ""),
                "bot_response": conv.get("bot_response", ""),
                "timestamp": conv.get("timestamp", "").isoformat() if conv.get("timestamp") else ""
            })
        
        return jsonify({"conversations": result})
    except Exception as e:
        logger.error(f"Erreur récupération conversations: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

if __name__ == '__main__':
    print(f"Login: http://localhost:5000/login")
    print(f" Devise: Franc CFA (FCFA)")
    
    app.run(
        debug=Config.DEBUG,
        host='0.0.0.0',
        port=5000
    )