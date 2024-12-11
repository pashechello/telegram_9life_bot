from telegram import ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup


def start_markup():
    return ReplyKeyboardMarkup([
        [
            KeyboardButton("🌀 Личный кабинет участника"),   
        ],
        [
            KeyboardButton("⭕️ Рейтинг победителей")
        ],       
        ],resize_keyboard=True)
    
def dashboard_markup():
    return InlineKeyboardMarkup([
    ])

def join_markup():
    return ReplyKeyboardMarkup([
        [KeyboardButton('✅ Участвовать')]
        
        ],resize_keyboard=True)

def admin_markup():
    return ReplyKeyboardMarkup([
    [
        KeyboardButton('📢 Рассылка'),
        KeyboardButton('📝 Изображение'),
        KeyboardButton('➕ Админ')
        
        
    ],
    [
        
        KeyboardButton('📊 Статистика'),
        KeyboardButton('👤 Юзер инфо'),
        KeyboardButton("ℹ️ Выгрузка")
    ],
    [
        KeyboardButton('🔄 Обновить конкурс'),
        KeyboardButton('✉️ Текст'),
        KeyboardButton('🖼 Изображение')
    ],
    [
        KeyboardButton('🔓 Открыть конкурс'),
        KeyboardButton('🔒 Закрыть конкурс')
    ],
    [
        KeyboardButton('🔙 Назад')
    ]
    ],resize_keyboard=True)
    
    
def cancel_markup():
    return ReplyKeyboardMarkup([
        [KeyboardButton('🚫 Завершить')]
    ],resize_keyboard=True)
    
def edit_shill_post_markup():
    return ReplyKeyboardMarkup([
        [
            KeyboardButton('SHILL - 1'),
            KeyboardButton('SHILL - 2'),
            KeyboardButton('SHILL - 3')
        ],
    [
        KeyboardButton('🔙 Назад')
    ]
    ],resize_keyboard=True)
