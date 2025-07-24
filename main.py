
import os
import logging
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ChatMemberHandler
)
from collections import defaultdict
from datetime import timedelta

# Configuración
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Groserías
GROSIAS = [
    "puta", "mierda", "cabron", "pendejo", "idiota", "imbecil", "malparido", "chingada",
    "verga", "coño", "joder", "gilipollas", "pelotudo", "culiao", "culero", "estupido", "zorra",
    "bitch", "fuck", "shit", "asshole", "dick", "bastard", "motherfucker", "slut", "cunt"
]

advertencias = defaultdict(int)
ultimos_usernames = {}

# Comandos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hola y gracias por unirte a nuestra comunidad. Estamos muy contentos de tenerte aquí.\n"
        "Antes de comenzar, por favor tómate un momento para leer nuestras reglas para mantener un ambiente respetuoso y productivo para todos:\n"
        "\n"
        "1. Respeto mutuo: Trata a todos los miembros con cortesía. No se tolerará lenguaje ofensivo, discriminación o acoso.\n"
        "2. Contenido apropiado: Comparte solo contenido relacionado con el propósito del grupo. Evita spam, publicidad no autorizada o material inapropiado.\n"
        "3. Privacidad: No compartas información personal tuya ni de otros sin consentimiento.\n"
        "4. Colaboración: Si tienes preguntas, dudas o aportes, compártelos con respeto.\n"
        "5. Moderación: Los administradores están para ayudar. Si necesitas asistencia, usa /ayuda.\n"
        "\n"
        "🆘 En cualquier momento puedes escribir /ayuda para contactar a los administradores.\n"
        "Gracias por formar parte de esta comunidad."
    )

async def reglas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "<b>Reglas del grupo:</b>\n"
        "1. Respeto mutuo entre todos los miembros.\n"
        "2. No se permite spam, contenido ofensivo o discriminatorio.\n"
        "3. Mantener el enfoque del grupo.\n"
        "4. No compartir información personal.\n"
        "5. Usa /ayuda si necesitas asistencia.",
        parse_mode="HTML"
    )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    admins = await context.bot.get_chat_administrators(chat.id)
    mensaje = f"🔔 El usuario @{update.effective_user.username or update.effective_user.first_name} ha solicitado ayuda en el grupo {chat.title}."

    for admin in admins:
        try:
            await context.bot.send_message(chat_id=admin.user.id, text=mensaje)
        except:
            pass

    await update.message.reply_text("✅ Hemos notificado a los administradores. Pronto te contactarán.")

async def staff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    admins = await context.bot.get_chat_administrators(chat.id)
    admin_list = "\n".join([f"• {admin.user.first_name} (@{admin.user.username})" if admin.user.username else f"• {admin.user.first_name}" for admin in admins])
    await update.message.reply_text(f"<b>Administradores del grupo:</b>\n{admin_list}", parse_mode="HTML")

# Manejo de groserías
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
                admins = await context.bot.get_chat_administrators(chat_id)
                for admin in admins:
                    try:
                        await context.bot.send_message(
                            chat_id=admin.user.id,
                            text=f"🔔 {update.effective_user.full_name} ha acumulado {advertencia_actual} advertencias."
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

# Manejo de cambio de nombre de usuario
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

# Main
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reglas", reglas))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("staff", staff))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), borrar_si_groseria))
    app.add_handler(ChatMemberHandler(detectar_cambio_username, ChatMemberHandler.CHAT_MEMBER))
    app.run_polling()
