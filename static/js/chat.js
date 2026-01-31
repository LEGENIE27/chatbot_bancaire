let currentToken = null;
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('fr-FR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

setInterval(updateCurrentTime, 1000);
updateCurrentTime();

async function startChat() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    currentToken = token;
    document.getElementById('authSection').classList.add('hidden');
    document.getElementById('chatSection').classList.remove('hidden');
    document.getElementById('quickActions').classList.remove('hidden');
    
    addMessage("Bonjour ! Je suis votre assistant bancaire. Comment puis-je vous aider aujourd'hui ?", false);
    loadChatHistory();
    
    document.getElementById('userInput').focus();
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message || !currentToken) return;
    addMessage(message, true);
    input.value = '';
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                token: currentToken
            })
        });
        
        const data = await response.json();
        
        hideTypingIndicator();
        
        if (response.ok) {
            addMessage(data.response, false, data.fraud_alert);
            if (data.fraud_alert) {
                showFraudAlert(data.risk_level);
            }
        } else {
            if (data.error === "Session invalide ou expirée") {
                addMessage("Session expirée. Veuillez vous reconnecter.", false);
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                addMessage("Désolé, une erreur s'est produite. Veuillez réessayer.", false);
            }
        }
    } catch (error) {
        console.error('Erreur:', error);
        hideTypingIndicator();
        addMessage("Erreur de connexion. Vérifiez votre connexion internet.", false);
    }
}
function quickAction(action) {
    const messages = {
        'solde': 'Quel est mon solde actuel ?',
        'transactions': 'Montre-moi mes dernières transactions',
        'carte': 'Je veux bloquer ma carte bancaire',
        'fraude': 'Je suspecte une fraude sur mon compte'
    };
    
    document.getElementById('userInput').value = messages[action];
    sendMessage();
}
function addMessage(text, isUser, isFraudAlert = false) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    if (isFraudAlert) {
        messageDiv.classList.add('fraud-alert');
    }
    
    const now = new Date();
    const timeString = now.toLocaleTimeString('fr-FR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <strong>${isUser ? 'Vous' : 'Assistant'}:</strong> ${text}
        </div>
        <div class="message-time">${timeString}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}
async function loadChatHistory() {
    if (!currentToken) return;
    
    try {
        const response = await fetch(`/api/chat/history?token=${currentToken}`);
        const data = await response.json();
        
        if (response.ok && data.history && data.history.length > 0) {
            const messagesContainer = document.getElementById('chatMessages');
            data.history.forEach(msg => {
                addMessage(msg.text, msg.is_user);
            });
        }
    } catch (error) {
        console.error('Erreur chargement historique:', error);
    }
}

function showFraudAlert(riskLevel) {
    const alertMessages = {
        'high': '🚨 Alerte de fraude de niveau ÉLEVÉ détectée!',
        'medium': '⚠️ Activité suspecte de niveau MOYEN détectée',
        'low': 'ℹ️ Comportement inhabituel détecté'
    };
    
    const alertMessage = alertMessages[riskLevel] || 'Activité suspecte détectée';
    alert(alertMessage);
}

document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('userInput');
    if (userInput) {
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
        startChat();
    }
});