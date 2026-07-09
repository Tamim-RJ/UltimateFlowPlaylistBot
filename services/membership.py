from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import User

from config import CHANNEL_USERNAME


async def check_membership(bot: Bot, user: User):
    if not CHANNEL_USERNAME:
        return True

    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest as exc:
        if "member not found" in str(exc).lower():
            return False
        raise