
import os
import json
from telegram.ext import Updater, MessageHandler, Filters
from telegram import Update
from telegram.ext import CallbackContext

# Cargar lista de groserías desde archivo
with open("badwords.json", "r", encoding="utf-8") as f:
    BAD_WORDS = set(json.load(f))

def detect_groserias(update: Update, context: CallbackContext):
    message_text = update.message.text.lower()
    if any(word in message_text for word in BAD_WORDS):
        try:
            context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=f"⚠️ Se eliminó un mensaje por contener lenguaje inapropiado.")
        except Exception as e:
            print("Error al borrar mensaje:", e)

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), detect_groserias))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
