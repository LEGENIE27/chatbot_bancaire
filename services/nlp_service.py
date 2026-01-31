import spacy
import re
from datetime import datetime

class NLPService:
    def __init__(self):
        self.nlp = spacy.load('fr_core_news_sm')
        self.intents = {
            'solde_compte': {
                'keywords': ['solde', 'montant', 'combien', 'reste', 'argent', 'compte'],
                'response': self._get_balance_response
            },
            'dernieres_transactions': {
                'keywords': ['transaction', 'historique', 'mouvement', 'opération', 'dernière'],
                'response': self._get_transactions_response
            },
            'bloquer_carte': {
                'keywords': ['bloquer', 'carte', 'perdue', 'volée', 'perte', 'vol'],
                'response': self._block_card_response
            },
            'fraude': {
                'keywords': ['fraude', 'suspicieux', 'anormal', 'arnaque', 'phishing', 'usurpation'],
                'response': self._fraud_alert_response
            },
            'contact_humain': {
                'keywords': ['conseiller', 'humain', 'parler', 'assistant', 'agent'],
                'response': self._human_assistant_response
            },
            'heure_ouverture': {
                'keywords': ['heure', 'ouverture', 'fermeture', 'horaire', 'ouvert'],
                'response': self._opening_hours_response
            }
        }
    
    def detect_intent(self, message):
        """Détecter l'intention du message"""
        doc = self.nlp(message.lower())
        best_intent = 'inconnu'
        best_score = 0
        
        for intent, data in self.intents.items():
            score = self._calculate_intent_score(doc, data['keywords'])
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent, best_score
    
    def _calculate_intent_score(self, doc, keywords):
        """Calculer le score d'intention"""
        score = 0
        message_text = doc.text
        
        for keyword in keywords:
            if keyword in message_text:
                score += 1
        
        return score / len(keywords) if keywords else 0
    
    def generate_response(self, intent, user_data=None):
        """Générer une réponse basée sur l'intention"""
        if intent in self.intents:
            return self.intents[intent]['response'](user_data)
        return self._unknown_response()
    
    def _get_balance_response(self, user_data):
        """Réponse pour le solde du compte avec format français"""
        if not user_data:
            return {
                'text': "Je ne peux pas accéder à vos informations de compte pour le moment.",
                'type': 'balance_info',
                'confidence': 0.95
            }
        balance = user_data.get('balance', 0)
        formatted_balance = f"{balance:,.2f} €".replace(',', ' ').replace('.', ',')
        message = f"**Votre solde actuel est de {formatted_balance}**"
        
        # Ajouter l'information carte bloquée si applicable
        card_status = user_data.get('card_status', 'active')
        if card_status == 'blocked':
            message += f"\n\n**Attention : Votre carte est actuellement bloquée.**"
            message += f"\nVeuillez contacter le service client au 09 70 80 90 60 pour la débloquer."
        
        message += f"\n\n_Cette information est mise à jour quotidiennement._"
        
        return {
            'text': message,
            'type': 'balance_info',
            'confidence': 0.95
        }
    
    def _get_transactions_response(self, user_data):
        return {
            'text': "Voici vos 5 dernières transactions:\n- 15/01: Amazon -45,99 €\n- 14/01: Salaire +2 500,00 €\n- 13/01: Supermarché -85,30 €\n- 12/01: Virement reçu +300,00 €\n- 11/01: Carburant -60,00 €",
            'type': 'transactions_list',
            'confidence': 0.90
        }
    
    def _block_card_response(self, user_data):
        return {
            'text': "Je peux vous aider à bloquer votre carte. Pour confirmer, veuillez répondre 'CONFIRMER BLOQUAGE'",
            'type': 'card_blocking',
            'requires_confirmation': True,
            'confidence': 0.85
        }
    
    def _fraud_alert_response(self, user_data):
        return {
            'text': " ALERTE: Transaction suspecte détectée! Un conseiller vous contactera dans les plus brefs délais. Voulez-vous bloquer temporairement votre carte en attendant?",
            'type': 'fraud_alert',
            'urgent': True,
            'confidence': 0.98
        }
    
    def _human_assistant_response(self, user_data):
        return {
            'text': "Je comprends que vous souhaitez parler à un conseiller. Je vous transfère immédiatement. Temps d'attente estimé: 2 minutes.",
            'type': 'human_transfer',
            'confidence': 0.92
        }
    
    def _opening_hours_response(self, user_data):
        return {
            'text': "Nos agences sont ouvertes:\n- Lundi au Vendredi: 9h-18h\n- Samedi: 9h-13h\n- Dimanche: Fermé\nService client: 24h/24 au 0 800 123 456",
            'type': 'info',
            'confidence': 1.0
        }
    
    def _unknown_response(self):
        return {
            'text': "Je n'ai pas bien compris votre demande. Pouvez-vous reformuler ou choisir parmi ces options:\n• Solde du compte\n• Dernières transactions\n• Bloquer une carte\n• Signaler une fraude\n• Horaires d'ouverture",
            'type': 'unknown',
            'confidence': 0.0
        }