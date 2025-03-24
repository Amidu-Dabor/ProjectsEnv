# services/general_chat_service/app.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

DATA_SERVICE_URL = "http://localhost:5004"
RESPONSE_SERVICE_URL = "http://localhost:5005"

@app.route('/general_query', methods=['POST'])
def general_query():
    data = request.json
    query = data.get("query", "")
    chat_history = data.get("chat_history", [])
    ds_resp = requests.post(f"{DATA_SERVICE_URL}/fetch_data", json={"query": query})
    context = ds_resp.json().get("data", "")
    payload = {"query": query + "\nContext: " + context, "mode": "general", "chat_history": chat_history}
    resp = requests.post(f"{RESPONSE_SERVICE_URL}/generate_response", json=payload)
    return jsonify(resp.json())

if __name__ == '__main__':
    app.run(port=5002, debug=True)
