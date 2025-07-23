
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

GROSIAS = [
    "puta", "mierda", "cabron", "pendejo", "idiota", "imbecil", "malparido", "chingada",
    "verga", "coño", "joder", "gilipollas", "pelotudo", "culiao", "culero", "estupido", "zorra",
    "bitch", "fuck", "shit", "asshole", "dick", "bastard", "motherfucker", "slut", "cunt"
]

async def borrar_si_groseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        texto = update.message.text.lower()
        if any(groseria in texto for groseria in GROSIAS):
            await update.message.delete()
            admin_ids = [admin.user.id for admin in await context.bot.get_chat_administrators(update.effective_chat.id)]
            for admin_id in admin_ids:
                try:
                    await context.bot.send_message(chat_id=admin_id, text=f"🛑 Se eliminó un mensaje con groserías de {update.effective_user.mention_html()}", parse_mode="HTML")
                except:
                    pass

if __name__ == '__main__':
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN no está definido en el entorno.")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), borrar_si_groseria))
    app.run_polling()
