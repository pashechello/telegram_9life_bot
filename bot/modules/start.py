from telegram import Update, ParseMode, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext, 
    MessageHandler, 
    CommandHandler, 
    ConversationHandler, 
    Filters, 
    CallbackQueryHandler  # Добавляем этот импорт
)
from bot import SUPPORT_CHANNEL, LOGGER, updater, dispatcher
from bot.modules.helper_funcs.text import ERROR, START_MESSAGE
from bot.modules.helper_funcs.decorators import send_action, contest
from bot.modules.helper_funcs.markup import start_markup
from bot.modules.sql.user_sql import get_users_id, add_referral, add_user
from bot.modules.sql.shill_sql import get_welcome

# Состояния диалога
VALIDATE, START_OVER = range(2)

# Ссылка на канал
CHANNEL_URL = "https://t.me/ztmvta"

# Inline-кнопка для подписки на канал
SUBSCRIBE_BUTTON = InlineKeyboardButton(text="✅ Подписаться на 9 Жизней", url=CHANNEL_URL)
JOIN_BUTTON = InlineKeyboardButton(text="✅ Участвовать в конкурсе", callback_data="join")

# Inline-клавиатура для подписки
SUBSCRIBE_MARKUP = InlineKeyboardMarkup([[SUBSCRIBE_BUTTON], [JOIN_BUTTON]])

# Идентификатор стикера
STICKER_ID = "CAACAgIAAxkBAAEK0rBnWICOB8ErBSctj6JREr_p3ki1dQACuWMAAks2wUrffFJ8FgGEFTYE"


@send_action(ChatAction.TYPING)
def start(update: Update, context: CallbackContext):
    context.user_data[START_OVER] = update.message
    
    # Отправляем стикер перед сообщением
    update.message.reply_sticker(sticker=STICKER_ID)
    
    # Отправляем приветственное сообщение со стандартной кнопкой "Участвовать"
    update.message.reply_text(
        START_MESSAGE,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[JOIN_BUTTON]])
    )
    return VALIDATE


def validate_user(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()  # Отвечаем на callback, чтобы убрать "загрузку"

    # Проверяем, подписан ли пользователь на канал
    is_in_grp = context.bot.get_chat_member(f"@{SUPPORT_CHANNEL}", update.effective_user.id)
    if is_in_grp.status not in ['member', 'creator', 'administrator']:
        # Если пользователь не подписан, отправляем сообщение с inline-кнопкой для подписки
        query.edit_message_text(
            ERROR,
            parse_mode=ParseMode.HTML,
            reply_markup=SUBSCRIBE_MARKUP
        )
        return VALIDATE

    # Если пользователь подписан, вызываем функцию valid_user
    valid_user(update, context)
    return -1


@send_action(ChatAction.TYPING)
@contest
def valid_user(update: Update, context: CallbackContext):
    data = context.user_data.get(START_OVER)
    welcome = get_welcome()
    ref_id = data.text[7:] if data else ""

    if ref_id and data and data.chat.id not in get_users_id():
        add_referral(int(ref_id))

    add_user(data)

    # Отправляем приветственное сообщение с изображением и текстом
    context.bot.send_photo(
        update.effective_message.chat_id,
        welcome.image,
        caption=welcome.text,
        parse_mode=ParseMode.HTML,
        reply_markup=start_markup()
    )
    return -1


@send_action(ChatAction.TYPING)
def back(update: Update, context: CallbackContext):
    context.bot.send_message(
        update.message.chat.id,
        f"Hey {update.message.chat.first_name}",
        reply_markup=start_markup()
    )


__mod_name__ = 'start'

# Обработчик для команды /start
START_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('start', start, pass_args=True)],
    states={
        VALIDATE: [
            MessageHandler(Filters.regex('^✅ Участвовать в конкурсе$'), validate_user, pass_user_data=True),
            CallbackQueryHandler(validate_user, pattern='^join$')
        ]
    },
    fallbacks=[]
)

# Обработчик для кнопки "Назад"
BACK_HANDLER = MessageHandler(Filters.regex('^🔙 Back$'), back)

dispatcher.add_handler(START_HANDLER)
dispatcher.add_handler(BACK_HANDLER)