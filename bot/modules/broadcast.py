from telegram import Update,ParseMode,ChatAction
from telegram.ext import CallbackContext,MessageHandler,CommandHandler,ConversationHandler,Filters,run_async
from telegram.error import Unauthorized

from bot import (LOGGER,SUPPORT_CHANNEL,dispatcher,updater)
from bot.modules.sql.user_sql import get_users_id,reset_score
from bot.modules.helper_funcs.decorators import send_action,admin_only
from bot.modules.helper_funcs.markup import cancel_markup,admin_markup

BOARDCAST=0

@admin_only
@send_action(ChatAction.TYPING)
def broadcast(update : Update,context : CallbackContext):
    context.bot.send_message(
        update.effective_message.chat_id,
        "Напиши волшебное сообщение для рассылки =)",
        reply_markup=cancel_markup()
    )
    return BOARDCAST

@send_action(ChatAction.TYPING)
def process_broadcast(update : Update,context : CallbackContext):
    LOGGER.info("Broadcast Started")
    for user in get_users_id() :
        try:
            context.bot.send_message(user,update.message.text)
            LOGGER.info(f"Mail sending to {user}")
        except Unauthorized:
            LOGGER.info(f"Failed Mail sending to {user}")
    context.bot.send_message(update.effective_message.chat_id,'Рассылка завершена!',reply_markup=admin_markup())
    LOGGER.info('Mailing finished!')
    
    return -1
    
@send_action(ChatAction.TYPING) 
def cancel_boardcast(update : Update,context : CallbackContext):
    context.bot.send_message(update.effective_message.chat_id,"Завершено",reply_markup=admin_markup())
    
    return -1

@send_action(ChatAction.TYPING)
@admin_only
def reset_contest(update : Update,context : CallbackContext):
    reset_score()
    context.bot.send_message(update.effective_message.chat_id,"<b>Sucessfully Reseted Contest</b>",reply_markup=admin_markup())

__mod_name__='boardcast'




BOARDCAST_HANDLER=ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('📢 Рассылка'),broadcast)],
    states={
        BOARDCAST:[MessageHandler(Filters.text & ~Filters.regex('^🚫 Выйти$'),process_broadcast)],
    
    },
    fallbacks=[MessageHandler(Filters.regex('^🚫 Завершить$'),cancel_boardcast)],
)

RESET_HANDLER=MessageHandler(Filters.regex('^🔄 Обновить конкурс$'),reset_contest)


dispatcher.add_handler(BOARDCAST_HANDLER)
dispatcher.add_handler(RESET_HANDLER)