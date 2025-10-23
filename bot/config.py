import os
from dotenv import load_dotenv

# Load .env for local dev (ignored in deployment)
load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# AI Keys
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

# Handles (use @ for Telegram links)
ADMIN_HANDLE = os.getenv("ADMIN_HANDLE", "@AAU_STUDENTSBOT")
MODULES_HANDLE = os.getenv("MODULES_HANDLE", "@Savvysocietybot")
CHANNEL_HANDLE = os.getenv("CHANNEL_HANDLE", "@Savvy_Society")

# Admin ID (for future use, e.g., admin commands)
ADMIN_ID = int(os.getenv("ADMIN_ID", "7075011101"))
