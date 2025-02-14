// Configuration
const API_URL = 'http://localhost:8000';
const userId = 'user_' + Math.random().toString(36).substr(2, 9);

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const statusElement = document.querySelector('.status');

// State
let sessionId = null;
let isWaitingForResponse = false;

// Helper Functions
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    indicator.id = 'typingIndicator';
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function setStatus(status) {
    statusElement.textContent = status;
}

async function startSession() {
    try {
        setStatus('Iniciando sesión...');
        const response = await fetch(`${API_URL}/start_session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId }),
        });

        if (!response.ok) {
            throw new Error('Failed to start session');
        }

        const data = await response.json();
        sessionId = data.session_id;
        
        // Enable input after session starts
        userInput.disabled = false;
        sendButton.disabled = false;
        setStatus('Conectado');
        
        // Add initial bot message
        addMessage(data.message);
    } catch (error) {
        console.error('Error starting session:', error);
        setStatus('Error de conexión');
    }
}

async function sendMessage(message) {
    if (!message.trim() || isWaitingForResponse) return;

    try {
        // Disable input while waiting for response
        isWaitingForResponse = true;
        userInput.disabled = true;
        sendButton.disabled = true;

        // Add user message
        addMessage(message, true);
        
        // Clear input
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();

        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                message: message
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to send message');
        }

        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add bot response
        addMessage(data.message);

        if (data.session_ended) {
            endSession();
        } else {
            // Re-enable input
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    } catch (error) {
        console.error('Error sending message:', error);
        setStatus('Error de conexión');
        removeTypingIndicator();
    } finally {
        isWaitingForResponse = false;
    }
}

async function endSession() {
    try {
        await fetch(`${API_URL}/end_session/${userId}`, {
            method: 'DELETE',
        });
        
        setStatus('Sesión finalizada');
        userInput.disabled = true;
        sendButton.disabled = true;
    } catch (error) {
        console.error('Error ending session:', error);
    }
}

// Event Listeners
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(userInput.value);
    }
});

sendButton.addEventListener('click', () => {
    sendMessage(userInput.value);
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (sessionId) {
        endSession();
    }
});

// Start session when page loads
startSession();