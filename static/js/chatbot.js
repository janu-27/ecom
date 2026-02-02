/**
 * AI Chatbot Widget
 * Powered by Gemini API
 */

class ChatbotWidget {
    constructor() {
        this.isOpen = false;
        this.isLoading = false;
        this.messageHistory = [];
        this.apiUrl = '/api/chatbot/';
        this.csrfToken = this.getCsrfToken();
        
        this.init();
    }

    init() {
        // Create HTML elements
        this.createElements();
        
        // Attach event listeners
        this.attachEventListeners();
        
        // Add initial greeting
        this.addBotMessage("Hi! 👋 I'm your AI Assistant. How can I help you today? Feel free to ask about our products, orders, or anything else!");
    }

    createElements() {
        // Create toggle button
        this.toggleBtn = document.createElement('button');
        this.toggleBtn.className = 'chatbot-toggle-btn';
        this.toggleBtn.innerHTML = '<i class="fas fa-comments"></i>';
        this.toggleBtn.setAttribute('aria-label', 'Open chatbot');
        document.body.appendChild(this.toggleBtn);

        // Create chatbot container
        this.container = document.createElement('div');
        this.container.className = 'chatbot-container';
        this.container.innerHTML = `
            <div class="chatbot-header">
                <h3>
                    <i class="fas fa-robot chatbot-header-icon"></i>
                    AI Assistant
                </h3>
                <button class="chatbot-close-btn" aria-label="Close chatbot">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="chatbot-messages"></div>
            <div class="chatbot-input-area">
                <input 
                    type="text" 
                    class="chatbot-input-field" 
                    placeholder="Type your message..."
                    autocomplete="off"
                >
                <button class="chatbot-send-btn" aria-label="Send message">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        `;
        document.body.appendChild(this.container);

        // Cache frequently used elements
        this.messagesDiv = this.container.querySelector('.chatbot-messages');
        this.inputField = this.container.querySelector('.chatbot-input-field');
        this.sendBtn = this.container.querySelector('.chatbot-send-btn');
        this.closeBtn = this.container.querySelector('.chatbot-close-btn');
    }

    attachEventListeners() {
        // Toggle button
        this.toggleBtn.addEventListener('click', () => this.toggle());

        // Close button
        this.closeBtn.addEventListener('click', () => this.close());

        // Send button
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Enter key to send
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.isOpen = true;
        this.container.classList.add('active');
        this.toggleBtn.classList.add('hidden');
        this.inputField.focus();
    }

    close() {
        this.isOpen = false;
        this.container.classList.remove('active');
        this.toggleBtn.classList.remove('hidden');
    }

    sendMessage() {
        const message = this.inputField.value.trim();

        if (!message) return;
        if (this.isLoading) return;

        // Add user message
        this.addUserMessage(message);

        // Clear input
        this.inputField.value = '';
        this.inputField.focus();

        // Show typing indicator
        this.showTypingIndicator();

        // Send to API
        this.fetchBotResponse(message);
    }

    addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chatbot-message user';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;
        
        messageDiv.appendChild(bubble);
        this.messagesDiv.appendChild(messageDiv);
        
        this.scrollToBottom();
        this.messageHistory.push({ role: 'user', content: text });
    }

    addBotMessage(text) {
        // Remove typing indicator if exists
        const typingIndicator = this.messagesDiv.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.parentElement.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = 'chatbot-message bot';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        // Parse markdown-like formatting
        bubble.innerHTML = this.parseText(text);
        
        messageDiv.appendChild(bubble);
        this.messagesDiv.appendChild(messageDiv);
        
        this.scrollToBottom();
        this.messageHistory.push({ role: 'bot', content: text });
        this.isLoading = false;
        this.updateInputState();
    }

    showTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chatbot-message bot';
        messageDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        this.messagesDiv.appendChild(messageDiv);
        this.scrollToBottom();
        this.isLoading = true;
        this.updateInputState();
    }

    async fetchBotResponse(userMessage) {
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                },
                body: JSON.stringify({ query: userMessage }),
                timeout: 15000 // 15 second timeout
            });

            // Check if response is ok
            if (!response.ok) {
                console.error('API Error:', response.status, response.statusText);
                this.addBotMessage("Sorry, there was a problem connecting to our AI. Please try again.");
                return;
            }

            const data = await response.json();

            // Always show response if success is true
            if (data.success && data.response) {
                this.addBotMessage(data.response);
            } else if (data.error) {
                this.addBotMessage("I'm having trouble understanding. Could you rephrase that?");
            } else {
                this.addBotMessage("I'm here to help! Ask me about our products, orders, or anything else.");
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            
            // More helpful error messages
            if (error.name === 'TypeError') {
                this.addBotMessage("Connection error. Please check your internet and try again.");
            } else {
                this.addBotMessage("I'm temporarily unavailable. Please try again in a moment.");
            }
        }
    }

    parseText(text) {
        // Escape HTML
        let escaped = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');

        // Convert URLs to links
        escaped = escaped.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" style="color: #0066cc; text-decoration: underline;">$1</a>'
        );

        // Convert **bold** to <strong>
        escaped = escaped.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Convert newlines to <br>
        escaped = escaped.replace(/\n/g, '<br>');

        return escaped;
    }

    updateInputState() {
        this.inputField.disabled = this.isLoading;
        this.sendBtn.disabled = this.isLoading;
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesDiv.scrollTop = this.messagesDiv.scrollHeight;
        }, 0);
    }

    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is on home page or a page that should have the chatbot
    const shouldInitChatbot = !window.location.pathname.includes('/admin/');
    
    if (shouldInitChatbot) {
        window.chatbot = new ChatbotWidget();
    }
});
