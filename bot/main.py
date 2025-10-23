from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from .config import BOT_TOKEN
from .handlers import start, handle_message


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set in environment variables.")

    # Build the bot app with timeouts for reliability
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
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
