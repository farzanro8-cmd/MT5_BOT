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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farm Monitor - Login</title>
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
            padding: 20px;
        }
        .login-box {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 40px 32px;
            width: 100%;
            max-width: 340px;
            text-align: center;
        }
        .login-box h2 {
            color: #4da6ff;
            font-size: 24px;
            margin-bottom: 6px;
            letter-spacing: 2px;
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
        input[type="password"]:focus { border-color: #4da6ff; }
        button {
            width: 100%;
            padding: 12px;
            background: #2ea043;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            letter-spacing: 1px;
        }
        button:hover { background: #3fb950; }
        .error {
            color: #f85149;
            font-size: 13px;
            margin-top: 14px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Farm</h2>
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farm Monitor</title>
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
            padding: 14px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
        }

        header h1 {
            font-size: 22px;
            color: #4da6ff;
            letter-spacing: 2px;
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
            gap: 12px;
            padding: 16px 20px;
            flex-wrap: wrap;
        }

        .stat-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px 16px;
            flex: 1;
            min-width: 90px;
            text-align: center;
        }

        .stat-card .value {
            font-size: 22px;
            font-weight: bold;
            color: #8b949e;
        }

        .stat-card .label {
            font-size: 11px;
            color: #8b949e;
            margin-top: 4px;
        }

        .log-container {
            margin: 0 20px 32px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
        }

        .log-header {
            background: #1c2128;
            padding: 10px 16px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
            color: #8b949e;
            flex-wrap: wrap;
            gap: 8px;
        }

        .log-list {
            max-height: 65vh;
            overflow-y: auto;
        }

        .log-item {
            padding: 10px 16px;
            border-bottom: 1px solid #21262d;
            display: flex;
            gap: 12px;
            align-items: flex-start;
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
            margin-top: 3px;
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
            font-size: 12px;
            min-width: 140px;
        }

        .log-msg {
            color: #c9d1d9;
            word-break: break-all;
            flex: 1;
        }

        .log-index {
            color: #30363d;
            min-width: 30px;
            text-align: right;
            font-size: 11px;
            flex-shrink: 0;
        }

        .empty {
            text-align: center;
            padding: 60px 20px;
            color: #8b949e;
            font-size: 14px;
        }

        .log-list::-webkit-scrollbar { width: 5px; }
        .log-list::-webkit-scrollbar-track { background: #161b22; }
        .log-list::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

        .refresh-btn {
            background: #2ea043;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 5px 14px;
            cursor: pointer;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        }
        .refresh-btn:hover { background: #3fb950; }

        /* mobile tweaks */
        @media (max-width: 480px) {
            header h1 { font-size: 18px; }
            .log-time { min-width: 100px; font-size: 11px; }
            .log-item { font-size: 12px; gap: 8px; }
            .stat-card .value { font-size: 18px; }
        }
    </style>
    <meta http-equiv="refresh" content="10">
</head>
<body>

<header>
    <h1>Farm</h1>
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
        <div class="value" style="font-size:13px; padding-top:4px;">{{ last_time }}</div>
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
                <div class="log-indicator {{ log.status }}"></div>
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

def compute_statuses(log_list):
    """
    آخرین لاگ همیشه active است.
    هر لاگ که فاصله زمانی بین آن و لاگ بعدی (جدیدتر) بیشتر از 0 ثانیه باشد
    و لاگ جدیدتری بعد از آن آمده باشد، inactive میشود.
    به عبارت ساده‌تر: فقط آخرین لاگ در هر "دسته زمانی متصل" active است —
    یعنی فقط آخرین لاگ کل لیست active است.
    """
    result = []
    for i, log in enumerate(log_list):
        if i == len(log_list) - 1:
            status = "active"
        else:
            status = "inactive"
        result.append({**log, "status": status})
    return result


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["auth"] = True
            return redirect(url_for("index"))
        return render_template_string(LOGIN_TEMPLATE, error=True)
    return render_template_string(LOGIN_TEMPLATE, error=False)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not session.get("auth"):
        return redirect(url_for("login"))
    last_time = logs[-1]["time"] if logs else "—"
    processed = compute_statuses(logs)
    return render_template_string(
        HTML_TEMPLATE,
        logs=list(reversed(processed)),
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
