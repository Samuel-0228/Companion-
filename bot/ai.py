import glob
import os
import traceback
from datetime import datetime
from openai import OpenAI
from .config import OPENAI_KEY, GROQ_KEY, ADMIN_HANDLE, MODULES_HANDLE, CHANNEL_HANDLE

# Clients
client_openai = None
if OPENAI_KEY:
    try:
        client_openai = OpenAI(api_key=OPENAI_KEY)
    except Exception:
        client_openai = None

client_groq = None
if GROQ_KEY:
    try:
        client_groq = OpenAI(
            api_key=GROQ_KEY, base_url="https://api.groq.com/openai/v1")
    except Exception:
        client_groq = None


def _log_error(user_message: str, notes: str, exc: Exception = None):
    """Log errors to data/error_log.txt (safe, no raises)."""
    try:
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        log_path = os.path.join(data_dir, "error_log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().isoformat()}] User: {user_message}\n")
            f.write(f"Notes: {notes}\n")
            if exc:
                f.write("Exception:\n")
                f.write("".join(traceback.format_exception(
                    type(exc), exc, exc.__traceback__)))
            f.write("-" * 80 + "\n")
    except Exception:
        pass  # Silent fail on logging


def save_to_results(user_message: str, bot_response: str):
    """Log convos to data/result.txt."""
    try:
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        log_path = os.path.join(data_dir, "result.txt")
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(
                f"[{datetime.utcnow().isoformat()}] User: {user_message}\n")
            log.write(f"Bot: {bot_response}\n")
            log.write("-" * 60 + "\n")
    except Exception as e:
        _log_error(user_message, "Failed to save result", e)


def load_aau_files() -> dict:
    """Load data/*.txt (exclude logs); {filename: text}."""
    files = sorted(glob.glob(os.path.join("data", "*.txt")))
    data_files = {}
    for file in files:
        name = os.path.basename(file)
        if name in ("result.txt", "error_log.txt"):
            continue
        key = os.path.splitext(name)[0]
        try:
            with open(file, "r", encoding="utf-8") as f:
                data_files[key] = f.read()
        except Exception as e:
            _log_error("", f"Failed reading {file}", e)
    return data_files


def call_model(client: OpenAI, model: str, system_prompt: str, user_message: str) -> str:
    """Call LLM; raises on error."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content.strip()


def local_search(user_message: str) -> str | None:
    """Keyword search in data/*.txt; return excerpt or None."""
    data_files = load_aau_files()
    if not data_files:
        return None

    tokens = [t.lower() for t in user_message.split() if len(t) > 2]
    if not tokens:
        return None

    scores = {}
    for key, text in data_files.items():
        lower_text = text.lower()
        count = sum(lower_text.count(tok) for tok in tokens)
        if count > 0:
            scores[key] = count

    if not scores:
        return None

    best_file = max(scores, key=scores.get)
    best_text = data_files.get(best_file, "")
    sentences = []
    for sent in best_text.splitlines():
        s_low = sent.lower()
        if any(tok in s_low for tok in tokens):
            if sent.strip():
                sentences.append(sent.strip())
        if len(sentences) >= 4:
            break

    if sentences:
        header = f"💡 Based on our AAU data ({best_file.replace('_', ' ').title()}):\n\n"
        return header + "\n".join(sentences)
    else:
        snippet = best_text.strip()[:1000].strip()
        if snippet:
            header = f"💡 Based on our AAU data ({best_file.replace('_', ' ').title()}):\n\n"
            return header + snippet
    return None


def generate_reply(user_message: str) -> str:
    """Pipeline: OpenAI > Groq > Local > Escalate."""
    # Compact AAU data for prompt
    aau_files = load_aau_files()
    aau_summary_parts = []
    for name, text in aau_files.items():
        snippet = text.strip()[:1000]
        aau_summary_parts.append(
            f"--- {name.replace('_', ' ').title()} ---\n{snippet}")

    aau_data_compact = "\n\n".join(aau_summary_parts)

    system_prompt = f"""
You are Savvy Chatbot — a helpful, concise assistant for Addis Ababa University (AAU) students.
Prefer AAU knowledge below for AAU questions; use general knowledge otherwise.

If about promotions, events, announcements, persons, or absent from AAU data: Direct to official bot {ADMIN_HANDLE}.
If about course modules/study materials: Direct to {MODULES_HANDLE}.
Be concise, avoid hallucinations; be transparent if uncertain.

AAU Knowledge (compact):
{aau_data_compact}
"""

    # 1. OpenAI
    if client_openai:
        try:
            bot_reply = call_model(
                client_openai, "gpt-4o-mini", system_prompt, user_message)
            full_reply = bot_reply + f"\n\n📢 {CHANNEL_HANDLE}"
            save_to_results(user_message, bot_reply)
            return full_reply
        except Exception as e:
            _log_error(user_message, "OpenAI failed", e)

    # 2. Groq
    if client_groq:
        try:
            bot_reply = call_model(
                client_groq, "llama-3.1-8b-instant", system_prompt, user_message)
            full_reply = bot_reply + f"\n\n📢 {CHANNEL_HANDLE}"
            save_to_results(user_message, bot_reply)
            return full_reply
        except Exception as e:
            _log_error(user_message, "Groq failed", e)

    # 3. Local
    try:
        local_result = local_search(user_message)
        if local_result:
            save_to_results(user_message, local_result)
            return local_result + f"\n\n📢 {CHANNEL_HANDLE}"
    except Exception as e:
        _log_error(user_message, "Local search failed", e)

    # 4. Escalate
    _log_error(user_message, "All layers failed", None)
    return f"⚠️ Couldn't find an answer. Contact admins: {ADMIN_HANDLE}"
