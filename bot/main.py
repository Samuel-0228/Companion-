from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from .config import BOT_TOKEN
from .handlers import start, handle_message
import logging

logger = logging.getLogger(__name__)


def add_handlers(application):
    """Add handlers to Application (for webhook in app.py or polling)."""
    logger.info("Adding handlers to bot application")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Handlers added successfully")


def main(polling=True):
    """Flexible: Polling for local dev, or build for webhook (returns app)."""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables.")

    # Build the app (v22 API)
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # Add handlers
    add_handlers(app)

    if polling:
        logger.info("🤖 Bot running in polling mode (local dev)...")
        app.run_polling(drop_pending_updates=True)
    else:
        logger.info("🤖 Application built for webhook mode.")
        return app  # Returned for external use (e.g., app.py)


if __name__ == "__main__":
    main(polling=True)  # Default: Polling for local runs
