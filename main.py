from textblob import TextBlob
import random
import spacy
from datetime import datetime

nlp = spacy.load("en_core_web_sm")

class SentientChatbot:
    def __init__(self):
        self.name = "Bot"            # sets the bot's name to "Bot"
        self.responses = {           # lists of possible responses top be randomly selected later
            "greeting": ["Hi there, ", "Hi there! ", "Hello, ", "Greetings! "],
            "greetingFollowUp": ["how can I help you today? ", "what's on your mind today? ", "how are you today? "],
            "positive": ["That's nice to hear.", "I'm glad you are so happy.", "It's nice to see this."],
            "negative": ["That's sorry to hear.", "I'm here for you."],
            "neutral": ["I see, tell me more.", "Interesting. Tell me more.", "Got it, how can I help you further? "]
        }
        self.followUps = {           # to keep the conversation going
            "positive": ["What's making you feel so good today? ", "Would you like to tell me why you're happy? "],
            "negative": ["What's been troubling you lately? ", "That's unfortunate, would you like to tell me about it?"],
            "neutral": ["Is there anything you would like to discuss? ", "Would you like to tell me more? "]
        }
        self.memory = []             # records chats
    
    def greet(self):             # synthesises greetings
        greeting = random.choice(self.responses("greeting"))
        if "," in greeting:
            return greeting + random.choice(self.responses("greetingFollowUp")).title()
        else:
            return greeting + random.choice(self.responses("greetingFollowUp"))
        
    def analyse(self, text):     # creates a polarity using the TextBlob analyser
        return TextBlob(text).sentiment.polarity

    def sentiment_type(self, polarity):     # creates a sentiment of P, Ne or Nu from polarity
        if polarity > 0.3: return "positive"
        if polarity < 0.3: return "negative"
        return "neutral"
        
    def process(self, text):    # compound function of analyse and sentiment_type
        polarity = self.analyse(text)
        sentiment = self.sentiment_type(polarity)

        self.memory.append({    # updates the chat with current time using the datetime library
            'text': text,
            'sentiment': sentiment,
            'time': datetime.now()
        })
            
        response = random.choice(self.responses[sentiment])

        if random.random() > 0.5: response += " " + random.choice(self.followUps[sentiment])
        # 50% chance to add a follow up to the response

        doc = nlp(text.lower())

        if any(token.text in ['hey', 'hi', 'hello'] for token in doc):
            response = self.greet() + " " + response
            
        # uses SpaCy to detect common greetings in the user's message

        entities = [(ent.text, ent.label_) for ent in nlp(text).ents]
        if entities:
            response += f"I noticed you mentioned {entities[0][0]}."
            
        # extracts the entitites e.g. people, places using spacy's nlp

        return response


def run_Chatbot():    # runs the chatbot
    print("Welcome to the Sentient Chatbot!")
    print("This chatbot can understand your feelings and respond accordingly.")
    Chatbot = SentientChatbot()
    print(f"{Chatbot.name}: {Chatbot.responses['greeting'][0]} {Chatbot.responses['greetingFollowUp'][0]}")
    print("Type 'exit chat' to stop the chat.")

    while True:
        user_input = input("You: ")
        if user_input == "exit chat":
            print(f"{Chatbot.name}: Goodbye!")
            break
        response = Chatbot.process(user_input)
        print(f"{Chatbot.name}: {response}")


if __name__ == '__main__':
    run_Chatbot()

