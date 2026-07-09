from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import ADMIN_ID
from database.queries import add_feedback, add_rating, add_song_request, get_or_create_user
from keyboards.admin import request_admin_keyboard
from keyboards.menu import back_menu, join_channel, main_menu
from services.membership import check_membership
from states.song_request import FeedbackState, SongRequest

router = Router()


def is_back_action(text: str | None) -> bool:
    return (text or "").strip() == "🔙 برگشت"


async def require_membership(event):
    joined = await check_membership(event.bot, event.from_user)
    if not joined:
        if isinstance(event, Message):
            await event.answer("برای استفاده از ربات اول عضو کانال شو 👇", reply_markup=join_channel)
        else:
            await event.message.answer("برای استفاده از ربات اول عضو کانال شو 👇", reply_markup=join_channel)
            await event.answer()
        return False
    return True


@router.message(F.text == "🎵 درخواست آهنگ")
async def request_song(message: Message, state: FSMContext):
    if not await require_membership(message):
        return

    await message.answer("🎵 اسم آهنگ یا خواننده رو بفرست:", reply_markup=back_menu)
    await state.set_state(SongRequest.waiting_for_song)


@router.message(SongRequest.waiting_for_song)
async def receive_song(message: Message, state: FSMContext):
    if not await require_membership(message):
        return

    if is_back_action(message.text):
        await state.clear()
        await message.answer("به منوی اصلی برگشتی 👋", reply_markup=main_menu)
        return

    song = (message.text or "").strip()
    if not song:
        await message.answer("لطفا اسم آهنگ یا خواننده رو بفرست.")
        return

    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    request = await add_song_request(user.id, song)

    await message.answer("درخواستت ثبت شد ✅\nبه زودی بررسی میشه 🎧")

    if ADMIN_ID:
        await message.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"درخواست جدید از کاربر @{user.username or message.from_user.full_name}\n\n🎵 {song}",
            reply_markup=request_admin_keyboard(request.id),
        )

    await state.clear()


@router.message(F.text == "💬 انتقاد و پیشنهاد")
async def feedback_start(message: Message, state: FSMContext):
    if not await require_membership(message):
        return

    await message.answer("پیامت رو بفرست تا برای ادمین ارسال بشه 👇", reply_markup=back_menu)
    await state.set_state(FeedbackState.waiting_for_feedback)


@router.message(FeedbackState.waiting_for_feedback)
async def receive_feedback(message: Message, state: FSMContext):
    if not await require_membership(message):
        return

    if is_back_action(message.text):
        await state.clear()
        await message.answer("به منوی اصلی برگشتی 👋", reply_markup=main_menu)
        return

    feedback_text = (message.text or "").strip()
    if not feedback_text:
        await message.answer("لطفا پیام خودت رو بنویس.")
        return

    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    await add_feedback(user.id, feedback_text)

    if ADMIN_ID:
        await message.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💬 پیام جدید از کاربر @{user.username or message.from_user.full_name}\n\n{feedback_text}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="👑 باز کردن پنل مدیریت", callback_data="admin_home")]]
            ),
        )

    await message.answer("پیامت ثبت شد ✅")
    await state.clear()


@router.message(F.text == "⭐ امتیاز به کانال")
async def request_rating(message: Message):
    if not await require_membership(message):
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐", callback_data="rate_1"),
                InlineKeyboardButton(text="⭐⭐", callback_data="rate_2"),
                InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3"),
            ],
            [
                InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4"),
                InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5"),
            ],
        ]
    )
    await message.answer("امتیازت رو انتخاب کن 🌟", reply_markup=keyboard)


@router.callback_query(F.data.startswith("rate_"))
async def set_rating(callback: CallbackQuery):
    if not await require_membership(callback):
        return

    score = int(callback.data.split("_", 1)[1])
    user = await get_or_create_user(callback.from_user.id, callback.from_user.username)
    await add_rating(user.id, score)

    if ADMIN_ID:
        await callback.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⭐ امتیاز جدید از کاربر @{user.username or callback.from_user.full_name}: {score} ستاره",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="👑 باز کردن پنل مدیریت", callback_data="admin_home")]]
            ),
        )

    await callback.message.edit_text(f"امتیاز {score} ستاره ثبت شد 🌟")
    await callback.answer()


@router.message(F.text == "🔎 جستجوی آهنگ")
async def search_placeholder(message: Message):
    if not await require_membership(message):
        return
    await message.answer("برای جستجو از دستور /search استفاده کن. مثال: /search شجریان")


@router.message(Command("search"))
async def search_command(message: Message):
    if not await require_membership(message):
        return

    query = (message.text or "").split(maxsplit=1)
    if len(query) < 2:
        await message.answer("مثال: /search شجریان")
        return

    await message.answer(f"جستجو برای «{query[1]}» ثبت شد. در نسخه بعدی نتیجه نمایش داده می‌شود.")


@router.message(F.text == "ℹ️ درباره کانال")
async def about_channel(message: Message):
    if not await require_membership(message):
        return

    await message.answer("این ربات برای دریافت و مدیریت درخواست آهنگ در کانال طراحی شده است 🎧")


@router.message(F.text == "🔙 برگشت")
async def back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("به منوی اصلی برگشتی 👋", reply_markup=main_menu)