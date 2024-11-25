# botapp/helpers.py
import random
import string
from botapp.models import ReferralCode
import logging

logger = logging.getLogger(__name__)

def generate_referral_code(length=6, max_attempts=1000):
    characters = string.ascii_letters + string.digits
    for attempt in range(max_attempts):
        code = ''.join(random.choices(characters, k=length))
        logger.debug(f"Generated referral code: {code}")
        if not ReferralCode.objects.filter(code=code).exists():
            logger.debug(f"Unique referral code found: {code}")
            return code
    raise Exception("Не удалось сгенерировать уникальный реферальный код после максимального количества попыток.")