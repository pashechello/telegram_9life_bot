# test_utils.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import AsyncMock, patch
from utils import check_subscription, calculate_winners_count, choose_winner
from database import Session, Participant

@pytest.mark.asyncio
async def test_check_subscription():
    context = AsyncMock()
    context.bot.get_chat_member = AsyncMock(return_value=AsyncMock(status="member"))

    result = await check_subscription(1, "-1001601093943", context)

    assert result is True

@pytest.mark.asyncio
async def test_check_subscription_error():
    context = AsyncMock()
    context.bot.get_chat_member = AsyncMock(side_effect=Exception("Test error"))

    result = await check_subscription(1, "-1001601093943", context)

    assert result is False

def test_calculate_winners_count():
    session = Session()
    session.query = lambda _: AsyncMock(count=lambda: 300)  # Увеличиваем количество участников до 300

    winners_count = calculate_winners_count()

    assert winners_count == 16  # 10 + (300 - 100) // 50 = 16

@pytest.mark.asyncio
async def test_choose_winner():
    context = AsyncMock()
    context.bot.get_chat_member = AsyncMock(return_value=AsyncMock(status="member"))

    session = Session()
    session.query = lambda _: AsyncMock(all=lambda: [Participant(user_id=i) for i in range(300)])  # Увеличиваем количество участников до 300

    winners = await choose_winner(context)

    assert len(winners) == 16  # 10 + (300 - 100) // 50 = 16