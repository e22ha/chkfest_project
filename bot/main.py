import os
import asyncio
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, Application
from dotenv import load_dotenv
from telegram.ext import ContextTypes

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Загрузка секретов из .env файла
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Константы для состояний разговора (можно добавить другие состояния по мере необходимости)
INPUT_FIO, INPUT_TITLE, INPUT_FILE = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.first_name}! Для участия в фотоконкурсе отправьте свои данные.\n"
        "Введите ваше ФИО:"
    )
    return INPUT_FIO


async def input_fio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['fio'] = update.message.text
    await update.message.reply_text(f"Спасибо, {context.user_data['fio']}!\nВведите название вашей работы:")
    return INPUT_TITLE


async def input_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['title'] = update.message.text
    await update.message.reply_text("Отправьте вашу работу (файл или архив):")
    return INPUT_FILE


async def input_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    file = await update.message.document.get_file()
    await file.download_to_drive(f"uploads/{user.id}_{context.user_data['fio']}_{context.user_data['title']}.jpg")

    await update.message.reply_text("Спасибо! Ваша заявка принята.")
    return ConversationHandler.END


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('new_application', start)],
        states={
            INPUT_FIO: {MessageHandler(filters.TEXT & ~filters.COMMAND, input_fio)},
            INPUT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_title)],
            INPUT_FILE: [MessageHandler(filters.Document.IMAGE, input_file)]
        },
        fallbacks=[]
    )
    application.add_handler(conversation_handler)

    asyncio.run(application.run_polling())


if __name__ == '__main__':
    main()
