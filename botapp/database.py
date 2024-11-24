from botapp.models import BotUser, ReferralCode, Participant
from botapp.helpers import generate_referral_code
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

def save_user(user, referral_code_rel=None):
    logger.debug(f"Сохранение пользователя: user_id={user.user_id}, referral_code_rel={referral_code_rel}")
    user_obj, created = BotUser.objects.get_or_create(
        user_id=user.user_id,
        defaults={
            'first_name': user.first_name,
            'last_name': user.last_name or '',
            'username': user.username or '',
            'referral_count': 0,
        }
    )
    if created:
        referral_code_rel = generate_referral_code()
        attempts = 0
        max_attempts = 1000
        while ReferralCode.objects.filter(code=referral_code_rel).exists() and attempts < max_attempts:
            referral_code_rel = generate_referral_code()
            attempts += 1
        if attempts == max_attempts:
            logger.error("Не удалось сгенерировать уникальный реферальный код.")
            return user_obj
        logger.debug(f"Генерация ReferralCode: {referral_code_rel} для пользователя {user_obj}")
        try:
            with transaction.atomic():
                ReferralCode.objects.create(user=user_obj, code=referral_code_rel)
                # Явно загружаем связанный объект ReferralCode
                user_obj = BotUser.objects.select_related('referral_code_rel').get(user_id=user.user_id)
                logger.debug(f"ReferralCode создан для пользователя {user_obj}")
        except Exception as e:
            logger.error(f"Ошибка при создании ReferralCode: {e}")
    else:
        logger.debug(f"Пользователь обновлен: {user_obj}")
    return user_obj

def add_participant(user_id, referral_code_rel=None):
    logger.debug(f"Добавление участника: user_id={user_id}, referral_code_rel={referral_code_rel}")
    try:
        user = BotUser.objects.get(user_id=user_id)
        if referral_code_rel:
            try:
                referral = ReferralCode.objects.get(code=referral_code_rel)
                participant, created = Participant.objects.get_or_create(user=user, referral_code=referral)
            except ReferralCode.DoesNotExist:
                logger.error(f"Referral code {referral_code_rel} not found.")
                participant, created = Participant.objects.get_or_create(user=user, referral_code=None)
        else:
            participant, created = Participant.objects.get_or_create(user=user, referral_code=None)
        if created:
            logger.debug(f"Участник создан: {participant}")
        else:
            logger.debug(f"Участник уже существует: {participant}")
        return participant
    except BotUser.DoesNotExist:
        logger.error(f"Пользователь с user_id={user_id} не найден.")
        raise ValueError(f"Пользователь с user_id={user_id} не найден.")
    except Exception as e:
        logger.error(f"Ошибка при добавлении участника: {e}")
        raise

def add_referral(referral_code_rel, referred_user_id):
    logger.debug(f"Adding referral: referral_code_rel={referral_code_rel}, referred_user_id={referred_user_id}")
    try:
        referrer = ReferralCode.objects.get(code=referral_code_rel).user
        referred_user = BotUser.objects.get(user_id=referred_user_id)
        if referrer == referred_user:
            logger.warning("User cannot refer themselves.")
            return None
        if not Referral.objects.filter(referrer=referrer, referred_user=referred_user).exists():
            referral = Referral.objects.create(referrer=referrer, referred_user=referred_user)
            referrer.referral_count += 1
            referrer.save()
            logger.debug(f"Referral created: {referral}")
            return referral
        else:
            logger.debug("Referral already exists")
            return None
    except ReferralCode.DoesNotExist:
        logger.error(f"Referral code {referral_code_rel} not found.")
        raise ValueError(f"Referral code {referral_code_rel} not found.")
    except BotUser.DoesNotExist:
        logger.error(f"User with user_id={referred_user_id} not found.")
        raise ValueError(f"User with user_id={referred_user_id} not found.")