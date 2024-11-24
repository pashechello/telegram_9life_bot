import os
import sys

# Добавьте корневую директорию проекта в sys.path
sys.path.append('/mnt/c/Users/PC/Desktop/WSL/999bot/project')

# Установите переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Инициализируйте Django
import django
django.setup()

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from botapp.handlers import (
    start, join_giveaway, check_subscription_after_subscribe,
    show_chances, show_referral_link, buy_product, show_prizes_count, handle_button,
    notify_participants, notify_winners, handle_referral
)
from botapp.config import BOT_TOKEN
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_bot():
    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()

        # Добавляем обработчики команд
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("referral", handle_referral))

        # Добавляем обработчики колбэков
        app.add_handler(CallbackQueryHandler(join_giveaway, pattern='^join_giveaway$'))
        app.add_handler(CallbackQueryHandler(check_subscription_after_subscribe, pattern='^check_subscription$'))

        # Добавляем обработчик текстовых сообщений
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))

        # Добавляем обработчики для других функций
        app.add_handler(CommandHandler("show_chances", show_chances))
        app.add_handler(CommandHandler("show_referral_link", show_referral_link))
        app.add_handler(CommandHandler("buy_product", buy_product))
        app.add_handler(CommandHandler("show_prizes_count", show_prizes_count))

        scheduler = AsyncIOScheduler()
        scheduler.add_job(notify_participants, 'date', run_date=datetime.now() + timedelta(days=1), args=[app])
        scheduler.add_job(notify_winners, 'date', run_date=datetime.now() + timedelta(days=2), args=[app])
        scheduler.start()

        app.run_polling()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)

if __name__ == "__main__":
    run_bot()