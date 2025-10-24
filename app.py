from flask import Flask, request
import os
import asyncio
import logging  # For structured logs
from telegram import Bot, Update  # Added Update import
from telegram.ext import ApplicationBuilder
from bot.config import BOT_TOKEN
from bot.main import add_handlers


app = Flask(__name__)
bot_app = None

# Enable logging (visible in Render)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def home():
    return "🤖 Savvy Chatbot is running on Render!"


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates (sync Flask + async bot)."""
    if bot_app is None:
        logger.error("Bot not initialized")
        return 'Bot not initialized', 500

    try:
        json_data = request.get_json(force=True)
        if not json_data:
            logger.warning("No JSON data in webhook")
            return 'No JSON data', 400

        logger.info(f"Webhook received: update_id={json_data.get('update_id', 'unknown')}")

        # Parse update (v22+ correct method: Use Update.de_json)
        update = Update.de_json(json_data, bot_app.bot)
        if update is None:
            logger.warning("Failed to parse update from JSON")
            return 'Invalid update', 400

        logger.info(f"Update parsed: chat_id={getattr(update, 'effective_chat', {}).id if update else 'None'}")

        # Async process in sync context
        async def _process_update():
            await bot_app.process_update(update)

        asyncio.run(_process_update())
        logger.info("Update processed successfully")
        return 'OK'
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'Error processing update', 500


def initialize_bot():
    """Build Application, add handlers, set webhook."""
    global bot_app
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables.")

    # Build with ApplicationBuilder (v22 API)
    bot_app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # Add handlers
    add_handlers(bot_app)

    # Set webhook URL (Render provides HTTPS)
    bot = Bot(BOT_TOKEN)
    hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if not hostname:
        raise ValueError("RENDER_EXTERNAL_HOSTNAME not set (Render env var).")
    webhook_url = f"https://{hostname}/webhook"
    bot.set_webhook(url=webhook_url)
    logger.info(f"✅ Webhook set to: {webhook_url}")


if __name__ == '__main__':
    # Initialize (sets webhook)
    initialize_bot()

    # Run Flask on PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
