
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN no está configurado. Asegúrate de establecer la variable de entorno.")

# Lista extensa de groserías (puedes seguir agregando más)
GROSERIAS = [
    "puta", "puto", "mierda", "cabron", "coño", "joder", "pendejo", "marica",
    "hijueputa", "imbécil", "gilipollas", "carajo", "culiao", "culero", "estupido",
    "idiota", "baboso", "boludo", "malparido", "perra", "chingada", "chinga", "verga"
]

async def eliminar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    if any(palabra in texto for palabra in GROSERIAS):
        try:
            await update.message.delete()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"🚫 El mensaje de @{update.message.from_user.username or update.message.from_user.first_name} fue eliminado por contener lenguaje inapropiado.")
        except Exception as e:
            print(f"Error al eliminar mensaje: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, eliminar_mensaje))
    print("🤖 Bot Antigroserías iniciado...")
    app.run_polling()
