from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from difflib import SequenceMatcher

class SelfLearningChatbot:
    def __init__(self):
        self.knowledge_base = {}

    def train(self, question, answer):
        self.knowledge_base[question.lower()] = answer

    def get_response(self, question):
        question = question.lower()
        if question in self.knowledge_base:
            return self.knowledge_base[question]
        else:
            return "I don't know the answer to that. Can you tell me?"

    def get_similar_response(self, question, similarity_threshold=0.9):
        question = question.lower()
        max_similarity = 0
        most_similar_question = None

        for known_question in self.knowledge_base:
            similarity = SequenceMatcher(None, question, known_question).ratio()
            if similarity > max_similarity and similarity >= similarity_threshold:
                max_similarity = similarity
                most_similar_question = known_question

        if most_similar_question is not None:
            return self.knowledge_base[most_similar_question]
        else:
            return None

    def save_model(self, file_path):
        with open(file_path, 'w') as file:
            for question, answer in self.knowledge_base.items():
                file.write(f"{question}:::{answer}\n")

    def load_model(self, file_path):
        if not os.path.exists(file_path):
            self.save_model(file_path)  # Create the file if it doesn't exist
        with open(file_path, 'r') as file:
            for line in file:
                question, answer = line.strip().split(":::")
                self.knowledge_base[question.lower()] = answer

# File path to store the knowledge base
knowledge_base_file = "knowledge_base.txt"

# Create the chatbot instance and load the model if available
chatbot = SelfLearningChatbot()
if os.path.exists(knowledge_base_file):
    chatbot.load_model(knowledge_base_file)

# Create a Flask app
app = Flask(__name__)
CORS(app, resources={r"/get_response": {"origins": "null"}})  # Allow requests from 'null'
CORS(app, resources={r"/save_response": {"origins": "null"}})  # Allow requests from 'null'

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_input = data['user_input']

    response = chatbot.get_similar_response(user_input, similarity_threshold=0.7)

    if response is None:
        # If no similar response found, ask for user response
        response = {"response": "I don't know the answer to that. Can you tell me?", "ask_for_answer": True}
    else:
        response = {"response": response, "ask_for_answer": False}

    return jsonify(response)

@app.route('/save_response', methods=['POST'])
def save_response():
    data = request.get_json()
    user_input = data['user_input'].lower()
    user_response = data['user_response']

    # Save the user_response to the knowledge_base or database
    chatbot.train(user_input, user_response)

    # Save the updated knowledge base to the file
    chatbot.save_model(knowledge_base_file)

    return jsonify({'status': 'success'}), 200

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
