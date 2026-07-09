import os

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from dotenv import load_dotenv

from database.queries import (
    block_user,
    count_requests,
    count_users,
    get_rating_stats,
    get_song_request,
    get_user,
    list_feedbacks,
    list_pending_requests,
    update_song_request_status,
)
from keyboards.admin import admin_main_keyboard, request_admin_keyboard

load_dotenv()

router = Router()


def get_admin_ids():
    raw_value = str(os.getenv("ADMIN_ID", "0")).strip()
    if not raw_value or raw_value == "0":
        return set()

    admin_ids = set()
    for part in raw_value.replace(" ", "").split(","):
        if part.isdigit():
            admin_ids.add(int(part))
    return admin_ids


def back_to_admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="↩️ بازگشت به پنل", callback_data="admin_home")]
        ]
    )


async def notify_admins(bot, text, reply_markup=None):
    for admin_id in get_admin_ids():
        await bot.send_message(chat_id=admin_id, text=text, reply_markup=reply_markup)


async def report_error(bot, user, context, exc):
    await notify_admins(
        bot,
        f"⚠️ خطا در بخش {context}\nکاربر: {getattr(user, 'id', 'unknown')} - {getattr(user, 'full_name', 'unknown')}\n{exc}",
    )


async def is_admin(user_id: int) -> bool:
    return user_id in get_admin_ids()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    try:
        if not await is_admin(message.from_user.id):
            await message.answer("این بخش فقط برای ادمین‌ها در دسترسه.")
            return
        await message.answer("👑 پنل مدیریت", reply_markup=admin_main_keyboard())
    except Exception as exc:
        await report_error(message.bot, message.from_user, "پنل ادمین", exc)
        await message.answer("خطایی در باز کردن پنل رخ داد.")


@router.message(F.text == "👑 پنل مدیریت")
async def admin_panel_text(message: Message):
    try:
        if not await is_admin(message.from_user.id):
            await message.answer("این بخش فقط برای ادمین‌ها در دسترسه.")
            return
        await message.answer("👑 پنل مدیریت", reply_markup=admin_main_keyboard())
    except Exception as exc:
        await report_error(message.bot, message.from_user, "پنل ادمین", exc)
        await message.answer("خطایی در باز کردن پنل رخ داد.")


@router.callback_query(F.data == "admin_home")
async def admin_home(callback: CallbackQuery):
    try:
        if not await is_admin(callback.from_user.id):
            return

        await callback.message.edit_text("👑 پنل مدیریت", reply_markup=admin_main_keyboard())
        await callback.answer()
    except Exception as exc:
        await report_error(callback.bot, callback.from_user, "بازگشت به پنل", exc)
        await callback.answer("خطایی رخ داد", show_alert=True)


@router.callback_query(F.data == "admin_requests")
async def admin_requests(callback: CallbackQuery):
    try:
        if not await is_admin(callback.from_user.id):
            return

        pending = await list_pending_requests()
        if not pending:
            await callback.message.edit_text("📭 درخواستی جدید وجود ندارد.", reply_markup=back_to_admin_keyboard())
            await callback.answer()
            return

        buttons = []
        for request in pending[:5]:
            buttons.append([
                InlineKeyboardButton(
                    text=f"#{request.id} - {request.song[:20]}",
                    callback_data=f"request_{request.id}",
                )
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="↩️ بازگشت", callback_data="admin_home")])
        await callback.message.edit_text("📨 درخواست‌های جدید:", reply_markup=keyboard)
        await callback.answer()
    except Exception as exc:
        await report_error(callback.bot, callback.from_user, "درخواست‌ها", exc)
        await callback.answer("خطایی رخ داد", show_alert=True)


@router.callback_query(F.data.startswith("request_"))
async def show_request_detail(callback: CallbackQuery):
    try:
        if not await is_admin(callback.from_user.id):
            return

        request_id = int(callback.data.split("_", 1)[1])
        request = await get_song_request(request_id)
        if request is None:
            await callback.message.edit_text("این درخواست دیگر موجود نیست.")
            return

        text = f"🆔 درخواست #{request.id}\n🎵 {request.song}\n📦 وضعیت: {request.status}"
        keyboard = request_admin_keyboard(request.id)
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="↩️ بازگشت", callback_data="admin_home")])
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    except Exception as exc:
        await report_error(callback.bot, callback.from_user, "جزئیات درخواست", exc)
        await callback.answer("خطایی رخ داد", show_alert=True)


@router.callback_query(F.data.startswith("approve_"))
async def approve_request(callback: CallbackQuery):
    try:
        if not await is_admin(callback.from_user.id):
            return

        request_id = int(callback.data.split("_", 1)[1])
        request = await get_song_request(request_id)
        if request is None:
            return

        await update_song_request_status(request_id, "approved")
        user = await get_user(request.user_id)
        if user is not None:
            await callback.bot.send_message(chat_id=user.telegram_id, text="درخواستت تایید شد ✅")

        await callback.message.edit_text(f"✅ درخواست #{request_id} تایید شد", reply_markup=back_to_admin_keyboard())
        await callback.answer("تایید شد")
    except Exception as exc:
        await report_error(callback.bot, callback.from_user, "تایید درخواست", exc)
        await callback.answer("خطایی رخ داد", show_alert=True)


@router.callback_query(F.data.startswith("reject_"))
async def reject_request(callback: CallbackQuery):
    try:
        if not await is_admin(callback.from_user.id):
            return

        request_id = int(callback.data.split("_", 1)[1])
        request = await get_song_request(request_id)
        if request is None:
            return

        await update_song_request_status(request_id, "rejected")
        user = await get_user(request.user_id)
        if user is not None:
            await callback.bot.send_message(chat_id=user.telegram_id, text="درخواستت رد شد ❌")

        await callback.message.edit_text(f"❌ درخواست #{request_id} رد شد", reply_markup=back_to_admin_keyboard())
        await callback.answer("رد شد")
    except Exception as exc:
        await report_error(callback.bot, callback.from_user, "رد درخواست", exc)
        await callback.answer("خطایی رخ داد", show_alert=True)


@router.callback_query(F.data.startswith("block_"))
async def block_request_user(callback: CallbackQuery):
    try:
        if not await is_admin(callback.from_user.id):
            return

        request_id = int(callback.data.split("_", 1)[1])
        request = await get_song_request(request_id)
        if request is None:
            return

        await block_user(request.user_id)
        await update_song_request_status(request_id, "rejected")
        user = await get_user(request.user_id)
        if user is not None:
            await callback.bot.send_message(chat_id=user.telegram_id, text="کاربر شما بلاک شد 🚫")

        await callback.message.edit_text(f"🚫 کاربر درخواست #{request_id} بلاک شد", reply_markup=back_to_admin_keyboard())
        await callback.answer("کاربر بلاک شد")
    except Exception as exc:
        await report_error(callback.bot, callback.from_user, "بلاک کاربر", exc)
        await callback.answer("خطایی رخ داد", show_alert=True)


@router.callback_query(F.data == "admin_feedback")
async def show_feedback(callback: CallbackQuery):
    try:
        if not await is_admin(callback.from_user.id):
            return

        feedbacks = await list_feedbacks()
        if not feedbacks:
            await callback.message.edit_text("💬 پیامی ثبت نشده است.", reply_markup=back_to_admin_keyboard())
            await callback.answer()
            return

        lines = [f"{feedback.id}. {feedback.message[:80]}" for feedback in feedbacks[:5]]
        await callback.message.edit_text("💬 پیام‌های اخیر:\n\n" + "\n".join(lines), reply_markup=back_to_admin_keyboard())
        await callback.answer()
    except Exception as exc:
        await report_error(callback.bot, callback.from_user, "پیام‌ها", exc)
        await callback.answer("خطایی رخ داد", show_alert=True)


@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    try:
        if not await is_admin(callback.from_user.id):
            return

        rating_stats = await get_rating_stats()
        users_count = await count_users()
        requests_count = await count_requests()

        text = (
            "📊 آمار ربات\n\n"
            f"👥 کاربران: {users_count}\n"
            f"🎵 درخواست‌ها: {requests_count}\n"
            f"⭐ میانگین امتیاز: {rating_stats['average']}\n"
            f"🗳 تعداد رای: {rating_stats['total_votes']}"
        )
        await callback.message.edit_text(text, reply_markup=back_to_admin_keyboard())
        await callback.answer()
    except Exception as exc:
        await report_error(callback.bot, callback.from_user, "آمار", exc)
        await callback.answer("خطایی رخ داد", show_alert=True)


@router.callback_query(F.data == "admin_broadcast")
async def broadcast_placeholder(callback: CallbackQuery):
    try:
        if not await is_admin(callback.from_user.id):
            return
        await callback.message.edit_text("📢 بخش ارسال همگانی در نسخه بعدی اضافه می‌شود.", reply_markup=back_to_admin_keyboard())
        await callback.answer()
    except Exception as exc:
        await report_error(callback.bot, callback.from_user, "ارسال همگانی", exc)
        await callback.answer("خطایی رخ داد", show_alert=True)