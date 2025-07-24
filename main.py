import os
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder, MessageHandler, filters, ContextTypes, ChatMemberHandler
)
from collections import defaultdict
import asyncio
from datetime import timedelta

GROSIAS = [
    "puta", "mierda", "cabron", "pendejo", "idiota", "imbecil", "malparido", "chingada",
    "verga", "coño", "joder", "gilipollas", "pelotudo", "culiao", "culero", "estupido", "zorra",
    "bitch", "fuck", "shit", "asshole", "dick", "bastard", "motherfucker", "slut", "cunt"
]

advertencias = defaultdict(int)
ultimos_usernames = {}

async def borrar_si_groseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        texto = update.message.text.lower()
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if any(groseria in texto for groseria in GROSIAS):
            await update.message.delete()

            advertencias[user_id] += 1
            advertencia_actual = advertencias[user_id]

            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ {update.effective_user.mention_html()} ha dicho una grosería.\nAdvertencia {advertencia_actual}/∞.",
                parse_mode="HTML"
            )

            if advertencia_actual % 4 == 0:
                admin_ids = [admin.user.id for admin in await context.bot.get_chat_administrators(chat_id)]
                for admin_id in admin_ids:
                    try:
                        await context.bot.send_message(
                            chat_id=admin_id,
                            text=f"🔔 {update.effective_user.full_name} ha acumulado {advertencia_actual} advertencias.",
                        )
                    except:
                        pass

            if advertencia_actual % 5 == 0:
                minutos = 5 + ((advertencia_actual - 5) // 5)
                until_date = update.message.date + timedelta(minutes=minutos)
                try:
                    await context.bot.restrict_chat_member(
                        chat_id=chat_id,
                        user_id=user_id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=until_date
                    )
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"🔇 {update.effective_user.mention_html()} ha sido silenciado por {minutos} minutos.",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"Error silenciando: {e}")

async def detectar_cambio_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member:
        user = update.chat_member.new_chat_member.user
        username_actual = user.username
        anterior_username = ultimos_usernames.get(user.id)

        if anterior_username and username_actual != anterior_username:
            try:
                await context.bot.send_message(
                    chat_id=update.chat_member.chat.id,
                    text=f"🔄 {user.full_name} ha cambiado su nombre de usuario.\nAntes: @{anterior_username or 'ninguno'}\nAhora: @{username_actual or 'ninguno'}"
                )
            except:
                pass

        ultimos_usernames[user.id] = username_actual

if __name__ == '__main__':
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN no está definido en el entorno.")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), borrar_si_groseria))
    app.add_handler(ChatMemberHandler(detectar_cambio_username, ChatMemberHandler.CHAT_MEMBER))
    app.run_polling()
