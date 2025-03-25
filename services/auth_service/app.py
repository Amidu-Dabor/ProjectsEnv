from flask import Flask, request, jsonify
import uuid
from typing import Dict
import os

app = Flask(__name__)

# Simulated user database and token store
USERS: Dict[str, str] = {"student": "password", "faculty": "faculty123"}
TOKENS: Dict[str, str] = {}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if username in USERS and USERS[username] == password:
        token = str(uuid.uuid4())
        TOKENS[token] = username
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/validate', methods=['POST'])
def validate():
    data = request.json
    token = data.get("token")
    if token in TOKENS:
        return jsonify({"status": "valid"})
    return jsonify({"error": "Invalid token"}), 401

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(port=port, debug=True)
