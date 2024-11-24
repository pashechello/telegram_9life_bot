import pytest
from django.test import TestCase
from botapp.models import User, Participant, Referral
from botapp.database import save_user, add_participant, add_referral
from telegram import User as TelegramUser
import os

@pytest.mark.django_db
class TestDatabaseFunctions(TestCase):

    def setUp(self):
        # Очистка базы данных перед каждым тестом
        Referral.objects.all().delete()
        Participant.objects.all().delete()
        User.objects.all().delete()

    def test_save_user(self):
        unique_user_id = 1000 + os.getpid()
        user = TelegramUser(unique_user_id, "Test", False, "TestUsername")
        referral_code = save_user(user)

        self.assertIsNotNone(referral_code)

        db_user = User.objects.get(user_id=unique_user_id)
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user.referral_code, referral_code)

        # Попытка сохранить того же пользователя снова должна вызвать ошибку
        with self.assertRaises(Exception):
            save_user(user)

    def test_add_participant(self):
        unique_user_id = 1000 + os.getpid()
        user = TelegramUser(unique_user_id, "Test", False, "TestUsername")
        referral_code = save_user(user)

        add_participant(unique_user_id, referral_code)

        participant = Participant.objects.get(user__user_id=unique_user_id)
        self.assertIsNotNone(participant)
        self.assertEqual(participant.referral_code, referral_code)

    def test_add_referral(self):
        referrer_unique_id = 1000 + os.getpid()
        referred_unique_id = referrer_unique_id + 1

        referrer_user = TelegramUser(referrer_unique_id, "ReferrerTest", False, "ReferrerUsername")
        referred_user = TelegramUser(referred_unique_id, "ReferredTest", False, "ReferredUsername")

        referrer_code = save_user(referrer_user)
        save_user(referred_user)

        add_referral(referrer_code, referred_unique_id)

        referral = Referral.objects.get(referred_user__user_id=referred_unique_id)
        self.assertIsNotNone(referral)
        self.assertEqual(referral.referrer.referral_code, referrer_code)

        referrer = User.objects.get(referral_code=referrer_code)
        self.assertEqual(referrer.referral_count, 1)