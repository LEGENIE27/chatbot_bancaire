import re
from datetime import datetime

class FraudDetectionService:
    def __init__(self):
        self.fraud_patterns = {
            'urgency_keywords': ['urgent', 'immédiat', 'rapide', 'tout de suite', 'urgence'],
            'secrecy_keywords': ['secret', 'confidentiel', 'personne', 'cache'],
            'payment_keywords': ['virement', 'paiement', 'transfert', 'argent', 'crypto'],
            'threat_keywords': ['problème', 'suspension', 'blocage', 'danger', 'risque']
        }
        
        self.suspicious_phrases = [
            r'votre compte.*suspend',
            r'cliquez.*lien',
            r'appelez.*immédiatement',
            r'ne dites.*personne',
            r'urgence.*virement'
        ]
    
    def analyze_message(self, message, user_context=None):
        """Analyser un message pour détecter des signes de fraude"""
        message_lower = message.lower()
        keyword_score = self._keyword_analysis(message_lower)
        pattern_score = self._pattern_analysis(message_lower)
        behavior_score = self._behavioral_analysis(user_context) if user_context else 0
        total_score = (keyword_score * 0.4) + (pattern_score * 0.4) + (behavior_score * 0.2)
        
        return {
            'is_fraudulent': total_score > 0.6,
            'confidence_score': total_score,
            'triggers': self._get_triggers(message_lower),
            'risk_level': self._get_risk_level(total_score)
        }
    
    def _keyword_analysis(self, message):
        """Analyse des mots-clés frauduleux"""
        score = 0
        total_keywords = 0
        
        for category, keywords in self.fraud_patterns.items():
            category_matches = sum(1 for keyword in keywords if keyword in message)
            total_keywords += len(keywords)
            score += category_matches
        
        return score / total_keywords if total_keywords > 0 else 0
    
    def _pattern_analysis(self, message):
        """Analyse des patterns suspects"""
        matches = 0
        for pattern in self.suspicious_phrases:
            if re.search(pattern, message):
                matches += 1
        
        return matches / len(self.suspicious_phrases)
    
    def _behavioral_analysis(self, user_context):
        """Analyse comportementale (à compléter)"""
        return 0.0
    
    def _get_triggers(self, message):
        """Identifier les déclencheurs spécifiques"""
        triggers = []
        for category, keywords in self.fraud_patterns.items():
            found_keywords = [keyword for keyword in keywords if keyword in message]
            if found_keywords:
                triggers.append({
                    'category': category,
                    'keywords': found_keywords
                })
        
        return triggers
    
    def _get_risk_level(self, score):
        """Déterminer le niveau de risque"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        elif score >= 0.4:
            return 'low'
        else:
            return 'none'