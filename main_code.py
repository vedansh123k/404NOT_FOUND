import json
import random
import re
import nltk
from nltk.stem import WordNetLemmatizer
import string

# Download necessary NLTK data
nltk.download('all')


class SimplePatternChatbot:
    def __init__(self, data_file='customer_support_data.json'):
        """
        Initialize the chatbot with the specified data file
        
        Parameters:
            data_file (str): Path to the JSON file containing intents data
        """
        # Load data
        with open(data_file, 'r') as file:
            self.data = json.load(file)
        
        # Initialize lemmatizer for word normalization
        self.lemmatizer = WordNetLemmatizer()
        
        # Preprocess patterns for all intents
        self.prepare_patterns()
        
        # Set fallback responses
        self.fallback_responses = [
            "I'm sorry, I don't understand. Could you please rephrase that?",
            "I'm not sure what you mean. Can you try asking in a different way?",
            "I didn't quite catch that. Could you please clarify?",
            "I'm still learning. Could you try asking your question differently?"
        ]
        
        # Track conversation context (for multi-turn conversations)
        self.context = {
            "current_intent": None,
            "previous_intents": []
        }
    
    def prepare_patterns(self):
        # Process all patterns for easier matching
        # Process each intent
        for intent in self.data['intents']:
            processed_patterns = []
            for pattern in intent['patterns']:
                # Create processed versions of each pattern
                processed = self.preprocess_text(pattern)
                processed_patterns.append(processed)
            
            # Store processed patterns with the intent
            intent['processed_patterns'] = processed_patterns
    
    def preprocess_text(self, text):
        """
        Preprocess text by:
        1. Converting to lowercase
        2. Tokenizing
        3. Removing punctuation
        4. Lemmatizing words
        5. Rejoining into a string
        """
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        tokens = nltk.word_tokenize(text)
        4
        # Remove punctuation and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in string.punctuation
        ]
        
        # Return as a string
        return " ".join(processed_tokens)
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        processed = self.preprocess_text(text)
        
        # Split by spaces
        words = processed.split()
        
        # Remove common words (simple approach)
        stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", 
                     "your", "yours", "yourself", "yourselves", "he", "him", "his", 
                     "himself", "she", "her", "hers", "herself", "it", "its", "itself", 
                     "they", "them", "their", "theirs", "themselves", "what", "which", 
                     "who", "whom", "this", "that", "these", "those", "am", "is", "are", 
                     "was", "were", "be", "been", "being", "have", "has", "had", "having", 
                     "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", 
                     "or", "because", "as", "until", "while", "of", "at", "by", "for", 
                     "with", "about", "against", "between", "into", "through", "during", 
                     "before", "after", "above", "below", "to", "from", "up", "down", 
                     "in", "out", "on", "off", "over", "under", "again", "further", 
                     "then", "once", "here", "there", "when", "where", "why", "how", 
                     "all", "any", "both", "each", "few", "more", "most", "other", 
                     "some", "such", "no", "nor", "not", "only", "own", "same", "so", 
                     "than", "too", "very", "s", "t", "can", "will", "just", "don", 
                     "should", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren", 
                     "couldn", "didn", "doesn", "hadn", "hasn", "haven", "isn", "ma", 
                     "mightn", "mustn", "needn", "shan", "shouldn", "wasn", "weren", 
                     "won", "wouldn"]
        
        keywords = [word for word in words if word not in stopwords]
        return keywords
    
    def keyword_match(self, user_input, pattern):
        """
        Match user input against a pattern based on keyword presence
        Returns a score of how well they match
        """
        user_keywords = set(self.extract_keywords(user_input))
        pattern_keywords = set(self.extract_keywords(pattern))
        
        # No useful keywords in either
        if len(user_keywords) == 0 or len(pattern_keywords) == 0:
            return 0
        
        # Calculate how many pattern keywords appear in user input
        matches = user_keywords.intersection(pattern_keywords)
        
        # Calculate score based on proportion of matched keywords
        score = len(matches) / len(pattern_keywords)
        return score
    
    def exact_match(self, preprocessed_input, processed_pattern):
        """Check if input matches pattern exactly"""
        return preprocessed_input == processed_pattern
    
    def find_intent(self, user_input):
        """Find the most likely intent for the user input"""
        processed_input = self.preprocess_text(user_input)
        
        # First check for exact matches
        for intent in self.data['intents']:
            for i, pattern in enumerate(intent['processed_patterns']):
                if self.exact_match(processed_input, pattern):
                    return intent, 1.0  # Perfect confidence
        
        # If no exact match, use keyword matching
        best_intent = None
        best_score = 0.3  # Threshold for minimum match quality
        
        for intent in self.data['intents']:
            for i, pattern in enumerate(intent['processed_patterns']):
                # Check original pattern too for more context
                original_pattern = intent['patterns'][i]
                score = self.keyword_match(user_input, original_pattern)
                
                if score > best_score:
                    best_score = score
                    best_intent = intent
        
        return best_intent, best_score
    
    def context_aware_response(self, user_input):
        """Generate a response considering conversation context"""
        # Find the intent
        intent, confidence = self.find_intent(user_input)
        
        # If we found a matching intent
        if intent is not None:
            # Update context
            if self.context["current_intent"]:
                self.context["previous_intents"].append(self.context["current_intent"])
                # Keep only last 3 intents
                if len(self.context["previous_intents"]) > 3:
                    self.context["previous_intents"].pop(0)
            
            self.context["current_intent"] = intent["tag"]
            
            # Generate response from the matched intent
            return random.choice(intent["responses"])
        else:
            # No intent matched
            return random.choice(self.fallback_responses)
    
    def get_response(self, user_input):
        """Generate a response to user input"""
        return self.context_aware_response(user_input)
    
    def reset_context(self):
        """Reset the conversation context"""
        self.context = {
            "current_intent": None,
            "previous_intents": []
        }

# Enhanced version with entity extraction
class EntityAwareChatbot(SimplePatternChatbot):
    def __init__(self, data_file='customer_support_data.json'):
        super().__init__(data_file)
        # Define entity patterns
        self.entity_patterns = {
            'order_number': r'order\s+(?:number|#)?\s*(\w{6,12})',
            'email': r'[\w\.-]+@[\w\.-]+\.\w+',
            'product_code': r'product\s+(?:code|#)?\s*(\w{3,10})',
            'date': r'(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?'
        }
        
        # Store extracted entities
        self.entities = {}
    
    def extract_entities(self, text):
        """Extract entities from text based on patterns"""
        found_entities = {}
        
        # Check each entity pattern
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Store the first matched entity of each type
                if isinstance(matches[0], tuple):
                    # For patterns with multiple capture groups
                    found_entities[entity_type] = matches[0]
                else:
                    found_entities[entity_type] = matches[0]
        
        # Update stored entities
        self.entities.update(found_entities)
        return found_entities
    
    def get_response(self, user_input):
        """Generate a response with entity recognition"""
        # Extract entities first
        entities = self.extract_entities(user_input)
        
        # Get base response
        response = super().get_response(user_input)
        
        # Enhance response with entity information if appropriate
        if entities and self.context["current_intent"]:
            # Add entity-specific information to responses
            if 'order_number' in entities and self.context["current_intent"] == "order_status":
                response += f" I've located your order #{entities['order_number']}. "
            
            elif 'email' in entities and self.context["current_intent"] == "returns":
                response += f" I'll send instructions to {entities['email']}. "
            
            elif 'product_code' in entities and self.context["current_intent"] == "product_info":
                response += f" I've found details for product {entities['product_code']}. "
        
        return response

# Sample JSON data structure (save as customer_support_data.json)
sample_data = {
    "intents": [
        {
            "tag": "greeting",
            "patterns": [
                "Hi", "Hello", "Hey", "Good morning", "Good afternoon", 
                "Hi there", "Hello there", "Hey there", "Greetings"
            ],
            "responses": [
                "Hello! How can I help you today?", 
                "Hi there! What can I assist you with?", 
                "Hey! How can I help?"
            ]
        },
        {
            "tag": "goodbye",
            "patterns": [
                "Bye", "See you later", "Goodbye", "Thanks, bye", "Exit", "End", 
                "That's all", "That will be all", "That's it", "I'm done", "Finished","Thank you"
            ],
            "responses": [
                "Goodbye! Have a great day!", 
                "Thanks for chatting. Bye!", 
                "See you soon!",
                "Your welcome :) "
            ]
        },
        {
            "tag": "returns",
            "patterns": [
                "How do I return an item?", "Return policy", "I want to return", 
                "Can I get a refund?", "How to exchange", "I need to send back", 
                "Can I send this back", "I don't want this anymore", "Return process", 
                "How long do I have to return", "Refund my order",
                "What is the return process if I receive a damaged or incorrect product? ",
                "How long does it take to process a refund? ","Can I exchange my order for a different item?",
                "Is there any additional charge for replacing a defective product?"
            ],
            "responses": [
                "You can return items within 30 days of purchase. Go to your order history and select 'Return item'.", 
                "Our return policy allows returns within 30 days. Visit the Returns page on our website.",
                "To start a return, log into your account, find your order, and click 'Return'. You'll receive a prepaid shipping label.",
                "We sincerely apologize for this issue. Please share images of the product, and we will process a replacement or refund based on our return policy.",
                "Refunds are typically processed within [time frame, e.g., 5-7 business days]. We will notify you once the refund is issued.",
                "Yes, exchanges are available based on our policy. Please share the details of the item you wish to exchange, and we will assist you further.",

            ]
        },
        {
            "tag": "order_status",
            "patterns": [
                "Where is my order?", "Track my package", "Order status", 
                "When will I receive my order?", "Is my order shipped yet", 
                "Has my order been shipped", "Package tracking", "Delivery status", 
                "When will my items arrive", "Check my order", "Find my order",
                "Could you provide an update on my order status?",
                "When can I expect my order to be delivered?",
                "Is there a way to track my order?",
                "What is the estimated delivery date for my order?",
                "My order is delayed. Could you explain the reason for the delay?",
                "Can I update the delivery address for my order?",
                "Is it possible to reschedule the delivery date?"
            ],
            "responses": [
                "You can check your order status by logging into your account and going to 'Order History'.", 
                "To track your package, please use the tracking number sent in your shipping confirmation email.",
                "Your order status can be found in your account under 'Order History'. You should also receive shipping updates via email.",
                "Certainly! Let me check your order details. Please provide your order number so I can assist you better.",
                "You can check it in orders details or you can track your order using the tracking link provided in your confirmation email.",
                "Yes! You can track your order by visiting tracking link sent to you or by entering your order number on our tracking page.",
                "We sincerely apologize for the delay. Your order has been delayed . We are working to get it delivered as soon as possible.",
                "If your order has not been dispatched yet, we can update the address. Please share the correct address at your earliest convenience."                 
            ]
        },
        {
            "tag": "payment",
            "patterns": [
                "What payment methods do you accept?", "Can I pay with PayPal?", 
                "Do you accept credit cards?", "Payment options", "Can I use Apple Pay", 
                "Do you accept debit cards", "Payment methods", "How can I pay", 
                "Do you take bank transfers", "Can I pay upon delivery",
                "I have made a payment, but my order is not confirmed. What should I do?",
                "Can I receive an invoice for my order?",
                "Do you offer Cash on Delivery (COD) as a payment option?",
                "How can I apply a discount code or coupon to my order?",
                "I was charged twice for my order. How can I request a refund for the extra charge?",
                "cash on delivery is available ?"
            ],
            "responses": [
                "We accept Visa, Mastercard, Credit Card , Debit Card , American Express, and PayPal.", 
                "You can pay using credit/debit cards or PayPal.",
                "Our payment options include all major credit cards, PayPal, and Apple Pay in selected countries.",
                "We apologize for the inconvenience. Please share your payment details, and we will verify the transaction and confirm your order.",
                "Certainly! Your invoice is available in your order confirmation email. If you need a separate copy, we can email it to you upon request.",
                "You can enter your discount code during checkout in the ‘Promo Code’ section. If you need assistance, please let us know.",
                "Yes, we do offer Cash on Delivery (COD) in select areas. Please check if your location is eligible during checkout."
            ]
        },
        {
            "tag": "contact",
            "patterns": [
                "How do I contact you", "Customer service number", "Email address", 
                "Contact information", "How can I reach you", "Phone number", 
                "Is there a live chat", "Talk to human", "Talk to agent", "Support contact",
                "How can I get in touch with customer support for assistance?",
                "I would like to file a complaint regarding my order. What is the procedure?",
                "Could you provide the contact details for a higher authority or escalation team?"
            ],
            "responses": [
                "You can reach our customer service team via E-mail or call us at our Customer Support Number.", 
                "Our customer service is available via email or phone call from 9 AM to 6 PM ET.",
                "The best way to reach us is by email. We typically respond within 24 hours.",
                "You can reach our support team via [email/phone/chat]. We are available from 9AM to 6PM on call to assist you. And, 24/7 via E-mail",
                "We are sorry for any inconvenience caused. Please Mail us or call on the support center number so that the relevant team can resolve the issue resolution.",
                "Certainly! If your issue requires further escalation, you may contact our escalation team ."
            ]
        },
        {
            "tag": "shipping",
            "patterns": [
                "Shipping options", "How long does shipping take", "Shipping cost", 
                "Free shipping", "International shipping", "Shipping to my country", 
                "Express delivery", "How fast can I get it", "Ship to multiple addresses",
                "Delivery time", "Expedited shipping"
            ],
            "responses": [
                "We offer standard shipping (3-5 business days), express shipping (1-2 business days), and international shipping (7-14 business days).", 
                "Standard shipping is free for orders over $50. Express shipping is available for an additional fee based on location.",
                "Shipping times vary by location. Standard shipping typically takes 3-5 business days within the continental INDIA."
            ]
        }
    ]
}

# Example usage
if __name__ == "__main__":
    # For demonstration, create a sample data file
    with open('customer_support_data.json', 'w') as f:
        json.dump(sample_data, f, indent=4)
    
    # Initialize simple chatbot
    # chatbot = SimplePatternChatbot()
    
    # Or use the entity-aware version for more advanced features
    chatbot = EntityAwareChatbot()
    
    print("Customer Support Chatbot")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Bot: Goodbye! Have a great day!")
            break
        
        response = chatbot.get_response(user_input)
        print(f"Bot: {response}")