
from textblob import TextBlob
import random
import spacy
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import os

# Initialize NLP and Flask app
nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)

class SentimentChatbot:
    def __init__(self):
        self.name = "EmoBot"
        self.responses = {
            'greetings': [
                "Hello! How are you feeling today?",
                "Hi there! What's on your mind?",
                "Greetings! How can I help you today?"
            ],
            'positive': [
                "That's wonderful to hear!",
                "I'm so glad you're feeling positive!",
                "Your happiness is contagious!"
            ],
            'negative': [
                "I'm sorry to hear that. Would you like to talk about it?",
                "That sounds difficult. I'm here to listen.",
                "I understand this is tough. Remember, I'm here for you."
            ],
            'neutral': [
                "I see. Tell me more.",
                "Interesting. What else is on your mind?",
                "Got it. How can I assist you further?"
            ]
        }
        self.follow_ups = {
            'positive': [
                "What's making you feel so good today?",
                "Would you like to share what brought you this happiness?"
            ],
            'negative': [
                "What's been troubling you lately?",
                "Would it help to talk more about what's bothering you?"
            ],
            'neutral': [
                "Is there anything specific you'd like to discuss?",
                "Can you tell me more about your current situation?"
            ]
        }
        self.memory = []
    
    def greet(self):
        return random.choice(self.responses['greetings'])
    
    def analyze_sentiment(self, text):
        return TextBlob(text).sentiment.polarity
    
    def get_sentiment_type(self, polarity):
        if polarity > 0.3: return 'positive'
        if polarity < -0.3: return 'negative'
        return 'neutral'
    
    def process_message(self, text):
        # Analyze sentiment
        polarity = self.analyze_sentiment(text)
        sentiment = self.get_sentiment_type(polarity)
        
        # Store in memory
        self.memory.append({
            'text': text,
            'sentiment': sentiment,
            'time': datetime.now()
        })
        
        # Generate base response
        response = random.choice(self.responses[sentiment])
        
        # 50% chance to add follow-up
        if random.random() > 0.5:
            response += " " + random.choice(self.follow_ups[sentiment])
        
        # Check for greetings
        doc = nlp(text.lower())
        if any(token.text in ['hi', 'hello', 'hey'] for token in doc):
            response = self.greet() + " " + response
        
        # Check for entities
        entities = [(ent.text, ent.label_) for ent in nlp(text).ents]
        if entities:
            response += f" By the way, I noticed you mentioned {entities[0][0]}."
        
        return response

# Initialize chatbot
chatbot = SentimentChatbot()

# Flask routes
@app.route('/')
def home():
    return render_template('chat.html', greeting=chatbot.greet())

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message.strip():
        return jsonify({'response': "Please type something..."})
    
    bot_response = chatbot.process_message(user_message)
    return jsonify({'response': bot_response})

# HTML Template

# Ensure template is always in the right place
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
os.makedirs(TEMPLATES_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>EmoBot - Sentiment Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        #chat-container {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        #chat-box {
            height: 300px;
            overflow-y: auto;
            margin-bottom: 15px;
            padding: 10px;
            border: 1px solid #eee;
            border-radius: 5px;
        }
        .user-message {
            background-color: #e3f2fd;
            padding: 8px 12px;
            border-radius: 15px;
            margin: 5px 0;
            max-width: 80%;
            float: right;
            clear: both;
        }
        .bot-message {
            background-color: #f1f1f1;
            padding: 8px 12px;
            border-radius: 15px;
            margin: 5px 0;
            max-width: 80%;
            float: left;
            clear: both;
        }
        #message-input {
            width: 75%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        #send-btn {
            width: 20%;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
         #send-btn:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div id="chat-container">
        <h2>EmoBot - Sentiment-Aware Chatbot</h2>
        <div id="chat-box"></div>
        <div>
            <input type="text" id="message-input" placeholder="Type your message...">
            <button id="send-btn">Send</button>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatBox = document.getElementById('chat-box');
            const messageInput = document.getElementById('message-input');
            const sendBtn = document.getElementById('send-btn');
            
            // Add initial greeting
            addBotMessage("{{ greeting }}");
            
            // Send message on button click
            sendBtn.addEventListener('click', sendMessage);
            
            // Send message on Enter key
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
            
            function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;
                
                // Add user message to chat
                addUserMessage(message);
                messageInput.value = '';
                
                // Send to server and get response
                fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                })
                .then(response => response.json())
                .then(data => {
                    addBotMessage(data.response);
                });
            }
            
            function addUserMessage(message) {
                const div = document.createElement('div');
                div.className = 'user-message';
                div.textContent = message;
                chatBox.appendChild(div);
                chatBox.scrollTop = chatBox.scrollHeight;
            }
            
            function addBotMessage(message) {
                const div = document.createElement('div');
                div.className = 'bot-message';
                div.textContent = message;
                chatBox.appendChild(div);
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        });
    </script>
</body>
</html>
"""

# Write the template file
with open(os.path.join(TEMPLATES_DIR, 'chat.html'), 'w') as f:
    f.write(HTML_TEMPLATE)

# Create template if it doesn't exist
import os
os.makedirs('templates', exist_ok=True)
with open('templates/chat.html', 'w') as f:
    f.write(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)

