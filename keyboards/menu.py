from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎵 درخواست آهنگ")],
        [KeyboardButton(text="💬 انتقاد و پیشنهاد")],
        [KeyboardButton(text="⭐ امتیاز به کانال")],
        [KeyboardButton(text="🔎 جستجوی آهنگ")],
        [KeyboardButton(text="ℹ️ درباره کانال")],
        [KeyboardButton(text="👑 پنل مدیریت")],
    ],
    resize_keyboard=True,
)

back_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔙 برگشت")
        ]
    ],
    resize_keyboard=True
)

join_channel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📢 عضویت در کانال",
                url="https://t.me/UltimateFlowPlaylist"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ بررسی عضویت",
                callback_data="check_join"
            )
        ]
    ]
)
