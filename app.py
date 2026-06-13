from flask import Flask, request, jsonify

app = Flask(__name__)

logs = []

@app.route("/")
def home():
    text = "<br>".join(logs[::-1])

    return f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="2">
    </head>
    <body style="background:black;color:lime;font-family:monospace">
        <h2>MT5 Bot Live Monitor</h2>
        {text}
    </body>
    </html>
    """

@app.route("/log", methods=["POST"])
def add_log():
    data = request.json
    logs.append(data["msg"])

    if len(logs) > 500:
        logs.pop(0)

    return jsonify({"status": "ok"})
