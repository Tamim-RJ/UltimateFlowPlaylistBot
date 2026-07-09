from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from database.queries import get_or_create_user
from keyboards.menu import join_channel, main_menu
from services.membership import check_membership

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message):
    await get_or_create_user(message.from_user.id, message.from_user.username)

    joined = await check_membership(message.bot, message.from_user)

    if not joined:
        await message.answer("برای استفاده از ربات اول عضو کانال شو 👇", reply_markup=join_channel)
        return

    await message.answer("سلام 👋\nبه ربات کانال خوش اومدی.", reply_markup=main_menu)


@router.callback_query(lambda c: c.data == "check_join")
async def check_join(callback: CallbackQuery):
    joined = await check_membership(callback.bot, callback.from_user)

    if joined:
        await callback.message.edit_text("عضویت تایید شد ✅")
        await callback.message.answer("حالا می‌تونی از ربات استفاده کنی 👍", reply_markup=main_menu)
    else:
        await callback.answer("هنوز عضو کانال نشدی ❌", show_alert=True)