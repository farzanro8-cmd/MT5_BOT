from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "mt5_monitor_secret_key_2024"

PASSWORD = "fr45rf"
logs = []
MAX_LOGS = 100

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farme Agent Monitor - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0d1117;
            color: #c9d1d9;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-box {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 40px;
            width: 340px;
            text-align: center;
        }
        .login-box h2 {
            color: #20c5b7;
            font-size: 20px;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }
        .login-box p {
            color: #8b949e;
            font-size: 13px;
            margin-bottom: 28px;
        }
        input[type="password"] {
            width: 100%;
            padding: 12px 16px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #c9d1d9;
            font-size: 15px;
            font-family: 'Courier New', monospace;
            outline: none;
            margin-bottom: 16px;
            text-align: center;
            letter-spacing: 4px;
        }
        input[type="password"]:focus {
            border-color: #20c5b7;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #20c5b7;
            color: #0d1117;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            letter-spacing: 1px;
        }
        button:hover { background: #1aa89b; }
        .error {
            color: #f85149;
            font-size: 13px;
            margin-top: 14px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>MT5 Bot Monitor</h2>
        <p>Enter password to continue</p>
        <form method="POST" action="/login">
            <input type="password" name="password" placeholder="••••••" autofocus>
            <button type="submit">ENTER</button>
            {% if error %}
            <div class="error">Wrong password. Try again.</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MT5 Bot Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background: #0d1117;
            color: #c9d1d9;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
        }

        header {
            background: #161b22;
            border-bottom: 1px solid #30363d;
            padding: 16px 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        header h1 {
            font-size: 20px;
            color: #20c5b7;
            letter-spacing: 1px;
        }

        .status-badge {
            background: #1a3a1a;
            color: #3fb950;
            border: 1px solid #3fb950;
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .dot {
            width: 8px; height: 8px;
            background: #3fb950;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .stats {
            display: flex;
            gap: 16px;
            padding: 20px 32px;
        }

        .stat-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 14px 24px;
            flex: 1;
            text-align: center;
        }

        .stat-card .value {
            font-size: 28px;
            font-weight: bold;
            color: #20c5b7;
        }

        .stat-card .label {
            font-size: 12px;
            color: #8b949e;
            margin-top: 4px;
        }

        .log-container {
            margin: 0 32px 32px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
        }

        .log-header {
            background: #1c2128;
            padding: 12px 20px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
            color: #8b949e;
        }

        .log-list {
            max-height: 600px;
            overflow-y: auto;
        }

        .log-item {
            padding: 10px 20px;
            border-bottom: 1px solid #21262d;
            display: flex;
            gap: 16px;
            align-items: center;
            font-size: 13px;
            transition: background 0.2s;
        }

        .log-item:hover { background: #1c2128; }
        .log-item:last-child { border-bottom: none; }

        .log-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
        }

        .log-indicator.active {
            background: #3fb950;
            box-shadow: 0 0 6px #3fb950;
        }

        .log-indicator.inactive {
            background: #2a2a2a;
            border: 1px solid #30363d;
        }

        .log-time {
            color: #8b949e;
            white-space: nowrap;
            min-width: 160px;
        }

        .log-msg { color: #c9d1d9; word-break: break-all; }

        .log-index {
            color: #30363d;
            min-width: 36px;
            text-align: right;
        }

        .empty {
            text-align: center;
            padding: 60px;
            color: #8b949e;
            font-size: 14px;
        }

        .log-list::-webkit-scrollbar { width: 6px; }
        .log-list::-webkit-scrollbar-track { background: #161b22; }
        .log-list::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

        .refresh-btn {
            background: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 5px 12px;
            cursor: pointer;
            font-size: 12px;
        }
        .refresh-btn:hover { background: #30363d; }
    </style>
    <meta http-equiv="refresh" content="10">
</head>
<body>

<header>
    <h1>MT5 Bot Monitor</h1>
    <div class="status-badge">
        <div class="dot"></div>
        LIVE
    </div>
</header>

<div class="stats">
    <div class="stat-card">
        <div class="value">{{ total }}</div>
        <div class="label">Total Logs</div>
    </div>
    <div class="stat-card">
        <div class="value">{{ last_time }}</div>
        <div class="label">Last Activity</div>
    </div>
    <div class="stat-card">
        <div class="value">{{ max_logs }}</div>
        <div class="label">Max Buffer</div>
    </div>
</div>

<div class="log-container">
    <div class="log-header">
        <span>Activity Log</span>
        <button class="refresh-btn" onclick="location.reload()">Refresh</button>
    </div>
    <div class="log-list">
        {% if logs %}
            {% for log in logs %}
            <div class="log-item">
                <span class="log-index">#{{ loop.revindex }}</span>
                <div class="log-indicator {% if loop.first %}active{% else %}inactive{% endif %}"></div>
                <span class="log-time">{{ log.time }}</span>
                <span class="log-msg">{{ log.msg }}</span>
            </div>
            {% endfor %}
        {% else %}
            <div class="empty">No logs received yet...</div>
        {% endif %}
    </div>
</div>

</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["auth"] = True
            return redirect(url_for("index"))
        return render_template_string(LOGIN_TEMPLATE, error=True)
    return render_template_string(LOGIN_TEMPLATE, error=False)

@app.route("/")
def index():
    if not session.get("auth"):
        return redirect(url_for("login"))
    last_time = logs[-1]["time"] if logs else "—"
    return render_template_string(
        HTML_TEMPLATE,
        logs=list(reversed(logs)),
        total=len(logs),
        last_time=last_time,
        max_logs=MAX_LOGS
    )

@app.route("/log", methods=["POST"])
def receive_log():
    data = request.get_json()
    if data:
        logs.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "msg": str(data.get("msg", data))
        })
        if len(logs) > MAX_LOGS:
            logs.pop(0)
    return jsonify({"status": "ok"})

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "log_count": len(logs)
    })

if __name__ == "__main__":
    app.run()
