import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from botapp.database import save_user, add_participant, add_referral
from botapp.models import BotUser, Participant, Referral
from botapp.utils import check_subscription, calculate_winners_count, choose_winner, participant_exists_async, get_referral_count_async, get_referral_code_async, get_referrals_async
from botapp.helpers import generate_referral_code
from asgiref.sync import sync_to_async
import asyncio

logger = logging.getLogger(__name__)

# Асинхронные обертки для синхронных функций
@sync_to_async
def save_user_async(user, referral_code_rel=None):
    try:
        save_user(user, referral_code_rel)
    except Exception as e:
        logger.error(f"Ошибка при сохранении пользователя: {e}", exc_info=True)

@sync_to_async
def add_participant_async(user_id, referral_code_rel):
    try:
        logger.debug(f"Adding participant async: user_id={user_id}, referral_code_rel={referral_code_rel}")
        add_participant(user_id, referral_code_rel)
    except Exception as e:
        logger.error(f"Ошибка при добавлении участника: {e}", exc_info=True)

@sync_to_async
def add_referral_async(referrer_code, referred_user_id):
    try:
        logger.debug(f"Adding referral async: referrer_code={referrer_code}, referred_user_id={referred_user_id}")
        referrer = BotUser.objects.get(referral_code_rel=referrer_code)
        referred_user = BotUser.objects.get(user_id=referred_user_id)
        logger.debug(f"Referrer found: {referrer.user_id}, Referred user found: {referred_user.user_id}")
        if not Referral.objects.filter(referrer=referrer, referred_user=referred_user).exists():
            Referral.objects.create(referrer=referrer, referred_user=referred_user)
            logger.debug(f"Referral created: referrer={referrer.user_id}, referred_user={referred_user.user_id}")
            referrer.referral_count += 1
            referrer.save()
            logger.debug(f"Referral count updated: referrer={referrer.user_id}, new count={referrer.referral_count}")
        else:
            logger.debug("Referral already exists")
    except BotUser.DoesNotExist:
        logger.error(f"Referrer or referred user does not exist: referrer_code={referrer_code}, referred_user_id={referred_user_id}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении реферала: {e}", exc_info=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        referral_code_rel = context.args[0] if context.args else None

        # Отправляем клавиатуру сразу после активации команды /start
        menu_keyboard = [
            [KeyboardButton("Мои шансы"), KeyboardButton("Пригласить")],
            [KeyboardButton("Призы"), KeyboardButton("В магазин")]
        ]
        menu_reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите действие:", reply_markup=menu_reply_markup)

        # Проверяем, участвует ли пользователь уже в конкурсе
        is_participant = await participant_exists_async(user.id)

        if is_participant:
            message = "Снова здравствуйте, чем я могу помочь? Воспользуйтесь клавишами меню для выбора раздела."
            await update.message.reply_text(message)
            return

        # Если пользователь не участвует, продолжаем обычную логику
        if not referral_code_rel:
            referral_code_rel = await get_referral_code_async(user.id)
            if not referral_code_rel:
                referral_code_rel = await sync_to_async(generate_referral_code)()
        await save_user_async(user, referral_code_rel)

        welcome_message = (
            "🎉 Добро пожаловать! 🎉\n\n"
            "Привет, {}! Рады видеть тебя в нашем боте.\n\n"
            "----------------------------------------\n"
            "Здесь ты найдешь много интересного!\n"
            "----------------------------------------\n"
            "Хочешь участвовать в розыгрыше?"
        ).format(user.first_name)

        welcome_keyboard = [
            [InlineKeyboardButton("Участвовать", callback_data='join_giveaway')],
        ]
        welcome_reply_markup = InlineKeyboardMarkup(welcome_keyboard)

        # Отправляем сообщение с инлайн-кнопками
        await update.message.reply_text(welcome_message, reply_markup=welcome_reply_markup)
    except Exception as e:
        logger.error(f"Ошибка в хэндлере start: {e}", exc_info=True)

async def join_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        referral_code_rel = await get_referral_code_async(user.id)
        if not referral_code_rel:
            referral_code_rel = await sync_to_async(generate_referral_code)()
        await save_user_async(user, referral_code_rel)

        message = "Чтобы участвовать в розыгрыше, нужно подписаться на канал '9 жизней'.\n\n"
        keyboard = [
            [InlineKeyboardButton("Подписаться", url='https://t.me/ztmvta')],
            [InlineKeyboardButton("Я уже подписан", callback_data='check_subscription')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(message, reply_markup=reply_markup)

        # Добавляем отладочный вывод
        logger.debug("Checking subscription")
        if await check_subscription(user.id, "-1001601093943", context):
            logger.debug("User is subscribed, adding participant")
            await add_participant_async(user.id, referral_code_rel)
        else:
            logger.debug("User is not subscribed")
    except Exception as e:
        logger.error(f"Ошибка в хэндлере join_giveaway: {e}", exc_info=True)

async def check_subscription_after_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        referral_code_rel = await get_referral_code_async(user.id)
        if not referral_code_rel:
            referral_code_rel = await sync_to_async(generate_referral_code)()
        await save_user_async(user, referral_code_rel)
        chat_id = "-1001601093943"  # Замените на ID вашего канала

        if await check_subscription(user.id, chat_id, context):
            await add_participant_async(user.id, referral_code_rel)
            await query.message.reply_text("Поздравляем, вы теперь участник розыгрыша!")
            referral_link = f"https://t.me/shop_9lifes_bot?start={referral_code_rel}"
            await query.message.reply_text(f"Если вы хотите повысить шансы на выигрыш, можете приглашать друзей! Вот ваша реферальная ссылка: {referral_link}")
        else:
            await query.message.reply_text("Похоже, вы не подписаны на канал. Пожалуйста, подпишитесь и нажмите 'Проверить подписку'.")
    except Exception as e:
        logger.error(f"Ошибка в хэндлере check_subscription_after_subscribe: {e}", exc_info=True)

async def show_chances(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.message.from_user.id
        chat_id = "-1001601093943"  # Замените на ID вашего канала

        is_subscribed = await check_subscription(user_id, chat_id, context)
        is_participant = await participant_exists_async(user_id)

        if not is_subscribed or not is_participant:
            message = "Похоже, вы не участвуете в розыгрыше, скорее подпишитесь на канал и повысьте шансы!"
            await update.message.reply_text(message)
            
            welcome_message = (
                "🎉 Добро пожаловать! 🎉\n\n"
                "Привет, {}! Рады видеть тебя в нашем боте.\n\n"
                "----------------------------------------\n"
                "Здесь ты найдешь много интересного!\n"
                "----------------------------------------\n"
                "Хочешь участвовать в розыгрыше?"
            ).format(update.effective_user.first_name)

            welcome_keyboard = [
                [InlineKeyboardButton("Участвовать", callback_data='join_giveaway')],
            ]
            welcome_reply_markup = InlineKeyboardMarkup(welcome_keyboard)

            await update.message.reply_text(welcome_message, reply_markup=welcome_reply_markup)
        else:
            referral_count = await get_referral_count_async(user_id)
            chances = 1 + referral_count
            
            if referral_count == 0:
                message = "Ура, у Вас есть 1 шанс выиграть! Приглашайте друзей и получайте по шансу за каждого друга!"
                referral_code_rel = await get_referral_code_async(user_id)
                referral_link = f"https://t.me/shop_9lifes_bot?start={referral_code_rel}"
                message += f"\n\nВаша реферальная ссылка: {referral_link}"
            else:
                message = f"Ого, у Вас целых {chances} шансов, желаем удачи!"
            
            await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Ошибка в хэндлере show_chances: {e}", exc_info=True)

async def show_referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.message.from_user.id
        chat_id = "-1001601093943"  # Замените на ID вашего канала

        is_subscribed = await check_subscription(user_id, chat_id, context)
        is_participant = await participant_exists_async(user_id)

        if not is_subscribed or not is_participant:
            message = "Подождите приглашать, Вы сами еще не участвуете в конкурсе."
            await update.message.reply_text(message)
            
            welcome_message = (
                "🎉 Добро пожаловать! 🎉\n\n"
                "Привет, {}! Рады видеть тебя в нашем боте.\n\n"
                "----------------------------------------\n"
                "Здесь ты найдешь много интересного!\n"
                "----------------------------------------\n"
                "Хочешь участвовать в розыгрыше?"
            ).format(update.effective_user.first_name)

            welcome_keyboard = [
                [InlineKeyboardButton("Участвовать", callback_data='join_giveaway')],
            ]
            welcome_reply_markup = InlineKeyboardMarkup(welcome_keyboard)

            await update.message.reply_text(welcome_message, reply_markup=welcome_reply_markup)
        else:
            referral_code_rel = await get_referral_code_async(user_id)
            referral_link = f"https://t.me/shop_9lifes_bot?start={referral_code_rel}"
            message = (
                f"Ваша реферальная ссылка: {referral_link}\n\n"
                "За каждого приглашенного пользователя вы получаете на 1 шанс выиграть больше."
            )
            await update.message.reply_text(message)

            referral_count = await get_referral_count_async(user_id)
            referrals = await get_referrals_async(referral_code_rel)

            if referral_count > 0:
                referral_list = "\n".join([f"{referral.first_name} {referral.last_name} (@{referral.username})" for referral in referrals])
                message = f"У вас {referral_count} рефералов:\n{referral_list}"
            else:
                message = "У вас пока нет рефералов."

            await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Ошибка в хэндлере show_referral_link: {e}", exc_info=True)

async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("Переход к покупке: http://t.me/shop_9lifes_bot/nevidimka")
    except Exception as e:
        logger.error(f"Ошибка в хэндлере buy_product: {e}", exc_info=True)

async def show_prizes_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        winners_count = await sync_to_async(calculate_winners_count)()
        await update.message.reply_text(f"На данный момент на кону {winners_count} Nevidimok!")
    except Exception as e:
        logger.error(f"Ошибка в хэндлере show_prizes_count: {e}", exc_info=True)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        text = update.message.text
        button_handlers = {
            "Мои шансы": show_chances,
            "Пригласить": show_referral_link,
            "Призы": show_prizes_count,
            "В магазин": buy_product
        }
        handler = button_handlers.get(text)
        if handler:
            await handler(update, context)
        else:
            await update.message.reply_text("Неизвестная команда. Пожалуйста, используйте клавиатуру.")
    except Exception as e:
        logger.error(f"Ошибка в хэндлере handle_button: {e}", exc_info=True)

async def notify_participants(context: ContextTypes.DEFAULT_TYPE):
    try:
        participants = await sync_to_async(list)(Participant.objects.all())
        winners_count = await sync_to_async(calculate_winners_count)()

        for participant in participants:
            user_id = participant.user.user_id
            referral_count = await get_referral_count_async(user_id)
            chances = 1 + referral_count
            referral_code_rel = await get_referral_code_async(user_id)
            referral_link = f"https://t.me/shop_9lifes_bot?start={referral_code_rel}"
            message = (
                f"До конца розыгрыша осталось всего 2 недели, а на кону уже целых {winners_count} NEVIDIMOK!\n"
                f"Напоминаю, что Ваши шансы на выигрыш равны = {chances}.\n"
                "Если хотите увеличить шансы, пригласите друзей!\n"
                f"Ваша реферальная ссылка: {referral_link}"
            )
            await context.bot.send_message(chat_id=user_id, text=message)
            await asyncio.sleep(1)  # Добавляем задержку между отправками
    except Exception as e:
        logger.error(f"Ошибка в хэндлере notify_participants: {e}", exc_info=True)

async def notify_winners(context: ContextTypes.DEFAULT_TYPE):
    try:
        participants = await sync_to_async(list)(Participant.objects.all())
        winners = await choose_winner(context)

        for winner in winners:
            user_id = winner.user_id
            message = "Ух, ты! Поздравляем, Вы выиграли NEVIDIMKY, напишите менеджеру @Antidronodeyalo, чтобы забрать приз!"
            await context.bot.send_message(chat_id=user_id, text=message)

        winners_list = "\n".join([str(winner.user_id) for winner in winners])
        for participant in participants:
            user_id = participant.user.user_id
            message = (
                f"Список победителей:\n{winners_list}\n\n"
                "В этот раз не повезло, но обязательно повезет в следующий! Не пропустите новый розыгрыш 9 Жизней"
            )
            await context.bot.send_message(chat_id=user_id, text=message)
    except Exception as e:
        logger.error(f"Ошибка в хэндлере notify_winners: {e}", exc_info=True)

async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        referral_code_rel = context.args[0] if context.args else None

        logger.debug(f"Handling referral for user: {user.id}, referral_code_rel: {referral_code_rel}")

        if referral_code_rel:
            referrer = await sync_to_async(BotUser.objects.filter(referral_code_rel=referral_code_rel).first)()
            if referrer:
                chat_id = "-1001601093943"  # Замените на ID вашего канала
                is_subscribed = await check_subscription(user.id, chat_id, context)
                is_participant = await participant_exists_async(user.id)
                is_already_referral = await sync_to_async(Referral.objects.filter(referred_user_id=user.id).exists)()

                logger.debug(f"User {user.id} subscription status: {is_subscribed}")
                logger.debug(f"User {user.id} participant status: {is_participant}")
                logger.debug(f"User {user.id} already referral status: {is_already_referral}")

                if is_subscribed and is_participant and not is_already_referral:
                    await add_referral_async(referral_code_rel, user.id)
                    await update.message.reply_text("Спасибо за участие! Ваш друг получил дополнительный шанс.")
                    referred_user = await sync_to_async(BotUser.objects.get)(user_id=user.id)
                    referred_user_name = f"{referred_user.first_name} {referred_user.last_name} (@{referred_user.username})"
                    message = f"Поздравляем! Ваш реферал {referred_user_name} успешно зарегистрировался, подписался на канал и принял участие в конкурсе."
                    await context.bot.send_message(chat_id=referrer.user_id, text=message)
                elif is_already_referral:
                    await update.message.reply_text("Вы уже являетесь рефералом.")
                else:
                    await update.message.reply_text("Для участия в конкурсе и получения дополнительного шанса, пожалуйста, подпишитесь на канал и примите участие в конкурсе.")
            else:
                await update.message.reply_text("Неверный реферальный код.")
        else:
            await start(update, context)
    except Exception as e:
        logger.error(f"Ошибка в хэндлере handle_referral: {e}", exc_info=True)