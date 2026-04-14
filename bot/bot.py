import asyncio
import logging
import os
import pathlib

# Загружаем .env если он есть (локальный запуск)
_env = pathlib.Path(__file__).parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
from config import TELEGRAM_BOT_TOKEN
from llm import get_reply

logging.basicConfig(level=logging.INFO)

# История диалогов: {chat_id: [{"role": ..., "content": ...}]}
conversations: dict[int, list[dict]] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conversations[chat_id] = []
    # Фил начинает разговор первым
    first_message = await _ask_fil(chat_id, "__START__")
    await update.message.reply_text(first_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text

    if chat_id not in conversations:
        conversations[chat_id] = []

    conversations[chat_id].append({"role": "user", "content": user_text})

    loop = asyncio.get_event_loop()
    reply = await loop.run_in_executor(None, get_reply, conversations[chat_id])

    conversations[chat_id].append({"role": "assistant", "content": reply})

    await update.message.reply_text(reply)


async def _ask_fil(chat_id: int, trigger: str) -> str:
    """Запускает первое сообщение от Фила при /start."""
    prompt = "Начни разговор с новым клиентом — первым, как описано в инструкции."
    conversations[chat_id].append({"role": "user", "content": prompt})
    loop = asyncio.get_event_loop()
    reply = await loop.run_in_executor(None, get_reply, conversations[chat_id])
    conversations[chat_id].append({"role": "assistant", "content": reply})
    return reply


def main():
    proxy = os.environ.get("SOCKS5_PROXY")
    builder = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).read_timeout(60).write_timeout(60).connect_timeout(60)
    if proxy:
        request = HTTPXRequest(proxy=proxy)
        builder = builder.request(request)
    app = builder.build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
