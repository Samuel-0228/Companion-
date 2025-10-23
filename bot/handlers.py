import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from .config import CHANNEL_HANDLE
from .ai import generate_reply


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_text = (
        "🤖 Hello! I’m Savvy Chatbot — your AAU AI assistant built by Savvy Society Coordinator.\n"
        f"🌐 Channel: {CHANNEL_HANDLE}\n\n"
        "Send me any question about Addis Ababa University or general topics!"
    )
    await update.message.reply_text(welcome_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages with AI reply."""
    user_text = (update.message.text or "").strip()
    if not user_text:
        await update.message.reply_text("Please send a text message.")
        return

    # Send placeholder
    working_msg = await update.message.reply_text("💭 Working on it...")

    # Run AI in thread (non-blocking)
    ai_response = await asyncio.to_thread(generate_reply, user_text)

    # Edit placeholder or fallback to new message
    try:
        await working_msg.edit_text(ai_response)
    except Exception:
        await update.message.reply_text(ai_response)
