import logging
import requests
from flask import Flask
from threading import Thread
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, MessageHandler, InlineQueryHandler, filters
from uuid import uuid4
import os

# Get bot token from environment (more secure)
BOT_TOKEN = os.getenv("BOT_TOKEN") or "7847727944:AAGhHHW2pIAu_qKoskfZU6wxtK_oCRWupwc"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Auto translate based on detected language
def auto_translate(text):
    try:
        detect_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={requests.utils.quote(text)}"
        response = requests.get(detect_url)
        data = response.json()
        detected_lang = data[2]

        target_lang = "uz" if detected_lang == "en" else "en"
        translate_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={requests.utils.quote(text)}"
        translated_data = requests.get(translate_url).json()

        translated = ''.join([item[0] for item in translated_data[0]])
        return translated, target_lang
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return "❌ Translation failed.", "en"

# /start command
async def start(update, context):
    await update.message.reply_text("👋 Welcome! Send a message or use inline mode like @YourBotName hello")

# Handle normal messages
async def handle_message(update, context):
    original = update.message.text
    translated, target_lang = auto_translate(original)
    await update.message.reply_text(translated)

# Handle inline queries
async def inline_query(update, context):
    query = update.inline_query.query.strip()
    if not query:
        return

    translated, target_lang = auto_translate(query)
    title = "🇺🇿" if target_lang == "uz" else "🇬🇧"

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"{title} {translated}",
            input_message_content=InputTextMessageContent(translated)
        )
    ]

    await update.inline_query.answer(results, cache_time=0)

# Main bot function
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(InlineQueryHandler(inline_query))

    application.run_polling()
    print("✅ Bot is running...")

# Flask keep-alive for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# Run bot and server
if __name__ == '__main__':
    keep_alive()
    main()