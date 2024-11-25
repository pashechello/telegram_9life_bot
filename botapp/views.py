#botapp/views.py
from django.shortcuts import render
from botapp.models import BotUser, ReferralCode, Participant, Referral
from botapp.database import save_user, add_participant, add_referral
from botapp.helpers import generate_referral_code
import logging

logger = logging.getLogger(__name__)

def test_view(request):
    try:
        user, created = BotUser.objects.get_or_create(
            user_id=12345,
            defaults={
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'username': 'ivanov',
                'referral_count': 0,
            }
        )
        referred_user, created = BotUser.objects.get_or_create(
            user_id=54321,
            defaults={
                'first_name': 'Петр',
                'last_name': 'Петров',
                'username': 'petrov',
                'referral_count': 0,
            }
        )
        referral_code = generate_referral_code()
        logger.debug(f"Сгенерирован реферальный код: {referral_code}")
        user_obj = save_user(user, referral_code)
        if user_obj.referral_code:
            referral_code_used = user_obj.referral_code.code
        else:
            referral_code_used = None
        logger.debug(f"Сохранен пользователь с реферальным кодом: {referral_code_used}")
        add_participant(user_obj.user_id, referral_code_used)
        logger.debug(f"Добавлен участник с реферальным кодом: {referral_code_used}")
        if referral_code_used:
            add_referral(referral_code_used, 54321)
            logger.debug(f"Добавлен реферал с реферальным кодом: {referral_code_used}")
        else:
            logger.warning("Нет доступного реферального кода для добавления реферала.")
        return render(request, 'test.html')
    except Exception as e:
        logger.error(f"Ошибка в test_view: {e}")
        return render(request, 'error.html', {'error': str(e)})