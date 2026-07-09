# UltimBot

A Telegram bot built with Aiogram 3 for music requests, feedback, ratings, and admin moderation.

## Features
- Main menu for requests, feedback, ratings, search, and channel info
- Channel membership check before use
- SQLite-backed storage with SQLAlchemy
- Admin panel for reviewing requests and viewing basic stats

## Setup
1. Clone the repository.
2. Create a virtual environment and install dependencies:
   - .venv\Scripts\python.exe -m pip install -r requirements.txt
3. Copy .env.example to .env and fill in your bot settings.
4. Run the bot:
   - .venv\Scripts\python.exe bot.py

## Environment variables
- BOT_TOKEN: Telegram bot token
- ADMIN_ID: Telegram user ID of the admin
- CHANNEL_USERNAME: Channel username for membership checks
- DATABASE_URL: Database connection string

## PostgreSQL on Railway
Use a PostgreSQL URL for `DATABASE_URL` in `.env`, for example:

```env
DATABASE_URL=postgresql+asyncpg://user:password@hostname:5432/database_name
```

If Railway provides a `postgres://...` URL, the bot normalizes it automatically to `postgresql+asyncpg://`.

## Notes
- The default local database is SQLite if `DATABASE_URL` is not set.
- For production deployment, set `DATABASE_URL` to your PostgreSQL connection string.
