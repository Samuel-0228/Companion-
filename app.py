from flask import Flask
import threading
import os
from bot.main import main  # Import bot runner

app = Flask(__name__)


@app.route('/')
def home():
    return "🤖 Savvy Chatbot is running on Render!"


def run_bot():
    main()  # Starts Telegram bot in polling mode


if __name__ == '__main__':
    # Run bot in background thread (non-blocking)
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Bind to deployment port (Render auto-sets PORT)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
