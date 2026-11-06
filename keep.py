from flask import Flask
import threading, os
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is online!"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000))), daemon=True).start()
exec(open('bot_v2.py').read())
