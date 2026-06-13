from flask import Flask, request, render_template_string

app = Flask(__name__)

# لیست برای ذخیره لاگ‌ها (در حافظه)
logs = []

# صفحه اصلی برای دیدن لاگ‌ها
@app.route('/')
def index():
    return render_template_string('''
        <html>
            <head><meta http-equiv="refresh" content="2"></head>
            <body>
                <h1>MT5 Bot Logs</h1>
                <pre>{{ logs|join('\n') }}</pre>
            </body>
        </html>
    ''', logs=logs)

# اندپوینت مورد نظر که 404 می‌دهد
@app.route('/log', methods=['POST'])
def log_endpoint():
    data = request.json
    msg = data.get('msg', '')
    logs.append(msg)
    # نگه داشتن فقط 50 لاگ آخر برای جلوگیری از پر شدن حافظه
    if len(logs) > 50:
        logs.pop(0)
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
