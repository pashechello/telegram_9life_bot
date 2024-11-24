#botapp/config.py 

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# Конфигурационные параметры
BOT_TOKEN = "7608856262:AAHFmEIgJjBca6eO9jUOSXwXUpSjbV41Gnk"
ADMIN_CHAT_ID = "-4517262101"
CHANNEL_ID = "-1001601093943"