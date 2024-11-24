#botapp/tests_handlers.py
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from telegram import Update, User, CallbackQuery, Message  # Правильный импорт
from telegram.ext import ContextTypes, CallbackContext
from botapp.handlers import start, join_giveaway, check_subscription_after_subscribe, show_chances, show_referral_link, buy_product, show_prizes_count, handle_button, notify_participants, notify_winners, handle_referral
from botapp.models import BotUser, Participant, Referral
from datetime import datetime, timezone
from botapp.helpers import generate_referral_code
from asgiref.sync import sync_to_async

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def clean_db(django_db_setup, django_db_blocker):
    # Очищаем таблицы перед каждым тестом
    with django_db_blocker.unblock():
        BotUser.objects.all().delete()
        Participant.objects.all().delete()
        Referral.objects.all().delete()

@pytest.fixture
def unique_user_id():
    return 1000 + os.getpid()  # Генерируем уникальный user_id для каждого теста

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_start():
    logger.debug("Starting test_start")
    update = MagicMock()
    update.effective_user = User(id=1, first_name="Test", is_bot=False, username="Test")
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_photo = AsyncMock()
    update.message.reply_video = AsyncMock()

    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)

    with patch('botapp.handlers.save_user_async', new_callable=AsyncMock) as mock_save_user:
        await start(update, context)

    update.message.reply_text.assert_called()
    mock_save_user.assert_called_once()
    logger.debug("test_start finished")

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_join_giveaway(unique_user_id):
    logger.debug("Starting test_join_giveaway")
    update = MagicMock()
    query = MagicMock()
    query.id = 1
    query.from_user = User(id=unique_user_id, first_name="Test", is_bot=False, username="Test")
    query.chat_instance = "test"
    query.answer = AsyncMock()
    query.message.reply_text = AsyncMock()
    update.callback_query = query
    update.effective_user = User(id=unique_user_id, first_name="Test", is_bot=False, username="Test")

    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)

    with patch('botapp.handlers.save_user_async', new_callable=AsyncMock) as mock_save_user, \
         patch('botapp.handlers.add_participant_async', new_callable=AsyncMock) as mock_add_participant, \
         patch('botapp.handlers.check_subscription', new_callable=AsyncMock, return_value=True):
        await join_giveaway(update, context)

    query.message.reply_text.assert_called()
    mock_save_user.assert_called_once()
    mock_add_participant.assert_called_once()
    logger.debug("test_join_giveaway finished")

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_check_subscription_after_subscribe(unique_user_id):
    logger.debug("Starting test_check_subscription_after_subscribe")
    update = MagicMock()
    query = MagicMock()
    query.id = 1
    query.from_user = User(id=unique_user_id, first_name="Test", is_bot=False, username="Test")
    query.chat_instance = "test"
    query.answer = AsyncMock()
    query.message.reply_text = AsyncMock()
    update.callback_query = query
    update.effective_user = User(id=unique_user_id, first_name="Test", is_bot=False, username="Test")

    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)

    with patch('botapp.handlers.save_user_async', new_callable=AsyncMock) as mock_save_user, \
         patch('botapp.handlers.check_subscription', new_callable=AsyncMock, return_value=True), \
         patch('botapp.handlers.add_participant_async', new_callable=AsyncMock) as mock_add_participant:
        await check_subscription_after_subscribe(update, context)

    query.message.reply_text.assert_called()
    mock_save_user.assert_called_once()
    mock_add_participant.assert_called_once()
    logger.debug("test_check_subscription_after_subscribe finished")

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_show_chances(unique_user_id):
    logger.debug("Starting test_show_chances")
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.from_user = User(id=unique_user_id, first_name="Test", is_bot=False, username="Test")
    update.message.chat = MagicMock()
    update.message.date = datetime.now(timezone.utc)

    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)

    with patch('botapp.handlers.check_subscription', new_callable=AsyncMock, return_value=True), \
         patch('botapp.handlers.participant_exists_async', new_callable=AsyncMock, return_value=True), \
         patch('botapp.handlers.get_referral_count_async', new_callable=AsyncMock, return_value=0):
        await show_chances(update, context)

    update.message.reply_text.assert_called()
    logger.debug("test_show_chances finished")

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_show_referral_link(unique_user_id):
    logger.debug("Starting test_show_referral_link")
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.from_user = User(id=unique_user_id, first_name="Test", is_bot=False, username="Test")
    update.message.chat = MagicMock()
    update.message.date = datetime.now(timezone.utc)

    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)

    with patch('botapp.handlers.check_subscription', new_callable=AsyncMock, return_value=True), \
         patch('botapp.handlers.participant_exists_async', new_callable=AsyncMock, return_value=True), \
         patch('botapp.handlers.get_referral_code_async', new_callable=AsyncMock, return_value='test_referral_code'), \
         patch('botapp.handlers.get_referrals_async', new_callable=AsyncMock, return_value=[]):
        await show_referral_link(update, context)

    update.message.reply_text.assert_called()
    logger.debug("test_show_referral_link finished")

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_buy_product(unique_user_id):
    logger.debug("Starting test_buy_product")
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.from_user = User(id=unique_user_id, first_name="Test", is_bot=False, username="Test")
    update.message.chat = MagicMock()
    update.message.date = datetime.now(timezone.utc)

    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)

    await buy_product(update, context)

    update.message.reply_text.assert_called_with("Переход к покупке: http://t.me/shop_9lifes_bot/nevidimka")
    logger.debug("test_buy_product finished")

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_show_prizes_count(unique_user_id):
    logger.debug("Starting test_show_prizes_count")
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.from_user = User(id=unique_user_id, first_name="Test", is_bot=False, username="Test")
    update.message.chat = MagicMock()
    update.message.date = datetime.now(timezone.utc)

    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)

    with patch('botapp.handlers.calculate_winners_count', return_value=10):
        await show_prizes_count(update, context)

    update.message.reply_text.assert_called()
    logger.debug("test_show_prizes_count finished")

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_handle_button(unique_user_id):
    logger.debug("Starting test_handle_button")
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.from_user = User(id=unique_user_id, first_name="Test", is_bot=False, username="Test")
    update.message.chat = MagicMock()
    update.message.date = datetime.now(timezone.utc)
    update.message.text = "Мои шансы"

    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)

    await handle_button(update, context)

    update.message.reply_text.assert_called()
    logger.debug("test_handle_button finished")

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_notify_participants():
    logger.debug("Starting test_notify_participants")
    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)

    # Создаем мок для участников
    participants_mock = [MagicMock(user_id=1)]

    with patch('botapp.handlers.sync_to_async', new_callable=AsyncMock, side_effect=lambda x: x), \
         patch('botapp.handlers.calculate_winners_count', return_value=16), \
         patch('botapp.handlers.get_referral_count_async', new_callable=AsyncMock, return_value=0), \
         patch('botapp.handlers.get_referral_code_async', new_callable=AsyncMock, return_value='test_referral_code'), \
         patch('botapp.models.Participant.objects.all', return_value=participants_mock):
        await notify_participants(context)

    # Проверяем, что send_message был вызван с правильными аргументами
    context.bot.send_message.assert_called_with(
        chat_id=1,
        text=(
            "До конца розыгрыша осталось всего 2 недели, а на кону уже целых 16 NEVIDIMOK!\n"
            "Напоминаю, что Ваши шансы на выигрыш равны = 1.\n"
            "Если хотите увеличить шансы, пригласите друзей!\n"
            "Ваша реферальная ссылка: https://t.me/shop_9lifes_bot?start=test_referral_code"
        )
    )
    logger.debug("test_notify_participants finished")

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_notify_winners():
    logger.debug("Starting test_notify_winners")
    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)

    winners = [MagicMock(user_id=1), MagicMock(user_id=2), MagicMock(user_id=3)]
    with patch('botapp.handlers.sync_to_async', side_effect=lambda x: x), \
         patch('botapp.handlers.choose_winner', new_callable=AsyncMock, return_value=winners), \
         patch('botapp.models.Participant.objects.all', return_value=[MagicMock(user_id=1)]):
        await notify_winners(context)

    context.bot.send_message.assert_called()
    logger.debug("test_notify_winners finished")

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_handle_referral(unique_user_id, monkeypatch):
    logger.debug("Starting test_handle_referral")
    update = MagicMock()
    update.effective_user = User(id=unique_user_id, first_name="Test", is_bot=False, username="Test")
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    application = MagicMock()
    application.bot = AsyncMock()
    context = CallbackContext(application, chat_id=123)
    context.args = ["referral_code"]

    # Mock database session and queries
    referrer_mock = MagicMock()
    referrer_mock.referral_code = "referral_code"
    referrer_mock.user_id = 999
    referred_user_mock = MagicMock()
    referred_user_mock.user_id = unique_user_id
    referred_user_mock.referral_code = await sync_to_async(generate_referral_code)()

    monkeypatch.setattr('botapp.models.BotUser.objects.filter', lambda **kwargs: MagicMock(first=lambda: referrer_mock))
    monkeypatch.setattr('botapp.models.Participant.objects.filter', lambda **kwargs: MagicMock(exists=lambda: True))
    monkeypatch.setattr('botapp.models.Referral.objects.filter', lambda **kwargs: MagicMock(exists=lambda: False))

    with patch('botapp.handlers.add_referral_async', new_callable=AsyncMock) as mock_add_referral, \
         patch('botapp.handlers.check_subscription', new_callable=AsyncMock, return_value=True):
        await handle_referral(update, context)

    update.message.reply_text.assert_called_with("Спасибо за участие! Ваш друг получил дополнительный шанс.")
    mock_add_referral.assert_called_once_with("referral_code", unique_user_id)
    logger.debug("test_handle_referral finished")