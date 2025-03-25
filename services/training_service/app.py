from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/train', methods=['POST'])
def train():
    data = request.json
    # Dummy training process; implement your training logic here if needed.
    return jsonify({"status": "Training started", "data_received": data})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5007))
    app.run(port=port, debug=True)
