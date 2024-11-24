import logging
from telegram.ext import ContextTypes
from botapp.models import BotUser, Participant
import random
import string
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

async def check_subscription(user_id, chat_id, context):
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        logger.debug(f"User {user_id} subscription status: {chat_member.status}")
        return chat_member.status in ['member', 'creator', 'administrator']
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}", exc_info=True)
        return False

@sync_to_async
def participant_exists_async(user_id):
    try:
        exists = Participant.objects.filter(user__user_id=user_id).exists()
        logger.debug(f"User {user_id} participant status: {exists}")
        return exists
    except Exception as e:
        logger.error(f"Ошибка при проверке наличия участника: {e}", exc_info=True)
        return False

def calculate_winners_count():
    """
    Вычисляет количество победителей на основе количества участников.
    """
    participants_count = Participant.objects.count()
    return 10 + max(0, (participants_count - 100) // 100)  # Изменено на 100

async def choose_winner(context: ContextTypes.DEFAULT_TYPE):
    """
    Выбирает победителей из списка участников.
    """
    participants = list(Participant.objects.all())
    winners_count = calculate_winners_count()

    if winners_count > len(participants):
        winners_count = len(participants)

    winners = random.sample(participants, winners_count)

    valid_winners = []
    for winner in winners:
        user_id = winner.user.user_id
        if await check_subscription(user_id, "-1001601093943", context):
            valid_winners.append(winner.user)
        else:
            logger.info(f"Пользователь {user_id} не подписан на канал.")

    logger.info(f"Выбраны победители: {valid_winners}")
    return valid_winners

@sync_to_async
def get_referral_count_async(user_id):
    try:
        return BotUser.objects.get(user_id=user_id).referral_count
    except BotUser.DoesNotExist:
        logger.error(f"Пользователь с user_id={user_id} не найден.")
        return 0
    except Exception as e:
        logger.error(f"Ошибка при получении количества рефералов: {e}", exc_info=True)
        return 0

@sync_to_async
def get_referral_code_async(user_id):
    try:
        user = BotUser.objects.get(user_id=user_id)
        return user.referral_code_rel.code if hasattr(user, 'referral_code_rel') else None
    except BotUser.DoesNotExist:
        logger.error(f"Пользователь с user_id={user_id} не найден.")
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении реферального кода: {e}", exc_info=True)
        return None

@sync_to_async
def get_referrals_async(referral_code_rel):
    try:
        return BotUser.objects.filter(referred_by__referrer__referral_code_rel=referral_code_rel)
    except Exception as e:
        logger.error(f"Ошибка при получении списка рефералов: {e}", exc_info=True)
        return []