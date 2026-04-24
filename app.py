from flask import Flask, request, jsonify, render_template
from model import ChatbotModel
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

chatbot = ChatbotModel("dataset.json")

@app.route('/')
def home():
    return render_template("index.html")
@app.route('/health')
def health():
    return "OK", 200
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    result = chatbot.get_response(user_input)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000, debug=True)