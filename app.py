from flask import Flask, request, jsonify

app = Flask(__name__)

logs = []

@app.route("/")
def index():
    return "<br>".join(logs) or "No logs yet"

@app.route("/log", methods=["POST"])
def receive_log():
    data = request.get_json()
    if data:
        logs.append(str(data))
    return jsonify({"status": "ok"})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run()
