import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes
from .config import CHANNEL_HANDLE
from .ai import generate_reply


logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    chat_id = update.effective_chat.id
    logger.info(f"Start command from chat_id: {chat_id}")

    welcome_text = (
        "🤖 Hello! I’m Savvy Chatbot — your AAU AI assistant built by Savvy Society Coordinator.\n"
        f"🌐 Channel: {CHANNEL_HANDLE}\n\n"
        "Send me any question about Addis Ababa University or general topics!"
    )
    await update.message.reply_text(welcome_text)
    logger.info(f"Sent welcome to {chat_id}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages with AI reply."""
    chat_id = update.effective_chat.id
    user_text = (update.message.text or "").strip()
    logger.info(f"Message from {chat_id}: '{user_text[:50]}...'")  # Truncate for logs

    if not user_text:
        await update.message.reply_text("Please send a text message.")
        logger.info(f"Empty message handled for {chat_id}")
        return

    # Send placeholder
    working_msg = await update.message.reply_text("💭 Working on it...")
    logger.info(f"Placeholder sent to {chat_id}")

    # Run AI in thread (non-blocking)
    try:
        ai_response = await asyncio.to_thread(generate_reply, user_text)
        logger.info(f"AI response generated for {chat_id} (len: {len(ai_response)})")
    except Exception as e:
        logger.error(f"AI generation failed for {chat_id}: {e}")
        ai_response = "⚠️ Sorry, an error occurred while processing your message."

    # Edit placeholder or fallback to new message
    try:
        await working_msg.edit_text(ai_response)
        logger.info(f"Edited response for {chat_id}")
    except Exception as e:
        await update.message.reply_text(ai_response)
        logger.warning(f"Fallback reply sent to {chat_id} due to edit error: {e}")
