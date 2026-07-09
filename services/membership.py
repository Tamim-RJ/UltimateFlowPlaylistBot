from aiogram import Bot
from aiogram.types import User

from config import CHANNEL_USERNAME


async def check_membership(bot: Bot, user: User):
    if not CHANNEL_USERNAME:
        return True

    member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
    return member.status in ["member", "administrator", "creator"]