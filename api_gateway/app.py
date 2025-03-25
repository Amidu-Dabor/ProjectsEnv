import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Use environment variables to override default endpoints.
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:5001")
GENERAL_CHAT_SERVICE_URL = os.environ.get("GENERAL_CHAT_SERVICE_URL", "http://localhost:5002")
STUDY_SUPPORT_SERVICE_URL = os.environ.get("STUDY_SUPPORT_SERVICE_URL", "http://localhost:5003")

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    mode = data.get("mode", "general")
    query_text = data.get("query", "")
    chat_history = data.get("chat_history", [])
    
    if mode == "study":
        # For study support, validate authentication
        auth_token = request.headers.get("Authorization")
        if not auth_token:
            return jsonify({"error": "Authentication token required"}), 401
        resp = requests.post(
            f"{STUDY_SUPPORT_SERVICE_URL}/study_query",
            json={"query": query_text, "chat_history": chat_history},
            headers={"Authorization": auth_token}
        )
        return jsonify(resp.json())
    else:
        # General enquiries
        resp = requests.post(
            f"{GENERAL_CHAT_SERVICE_URL}/general_query",
            json={"query": query_text, "chat_history": chat_history}
        )
        return jsonify(resp.json())

if __name__ == '__main__':
    app.run(port=5000, debug=True)
