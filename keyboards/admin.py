from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📨 درخواست‌ها", callback_data="admin_requests")],
            [InlineKeyboardButton(text="💬 پیام‌ها", callback_data="admin_feedback")],
            [InlineKeyboardButton(text="📊 آمار", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📢 ارسال همگانی", callback_data="admin_broadcast")],
        ]
    )


def request_admin_keyboard(request_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ تایید", callback_data=f"approve_{request_id}"),
                InlineKeyboardButton(text="❌ رد", callback_data=f"reject_{request_id}"),
            ],
            [InlineKeyboardButton(text="🚫 بلاک", callback_data=f"block_{request_id}")],
        ]
    )