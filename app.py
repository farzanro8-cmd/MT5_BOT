from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
from collections import deque

app = Flask(__name__)

# نگه‌داری آخرین 200 لاگ در حافظه
logs = deque(maxlen=200)

HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="10">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MT5 Bot Monitor</title>
  <style>
    body { font-family: Tahoma, sans-serif; background: #0f0f0f; color: #e0e0e0; padding: 16px; }
    h1   { color: #00d4aa; font-size: 1.2rem; }
    .log { background: #1a1a1a; border-left: 3px solid #00d4aa;
           margin: 6px 0; padding: 8px 12px; border-radius: 4px;
           font-size: 0.85rem; word-break: break-all; }
    .time { color: #888; font-size: 0.75rem; margin-left: 8px; }
    .empty { color: #555; }
  </style>
</head>
<body>
  <h1>MT5 Bot Monitor</h1>
  <p style="color:#555; font-size:0.8rem;">آخرین بروزرسانی: {{ now }} | صفحه هر ۱۰ ثانیه رفرش می‌شود</p>
  {% if logs %}
    {% for entry in logs|reverse %}
      <div class="log">
        <span class="time">{{ entry.time }}</span>
        {{ entry.msg }}
      </div>
    {% endfor %}
  {% else %}
    <p class="empty">هنوز لاگی دریافت نشده...</p>
  {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        HTML,
        logs=list(logs),
        now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    )

@app.route("/log", methods=["POST"])
def receive_log():
    data = request.get_json(silent=True)
    if not data or "msg" not in data:
        return jsonify({"error": "invalid payload"}), 400

    entry = {
        "time": datetime.utcnow().strftime("%H:%M:%S"),
        "msg":  str(data["msg"])
    }
    logs.append(entry)
    print(f"[LOG] {entry['time']} | {entry['msg']}")
    return jsonify({"status": "ok"}), 200

@app.route("/health")
def health():
    return jsonify({"status": "alive", "log_count": len(logs)}), 200

if __name__ == "__main__":
    app.run(debug=False)
