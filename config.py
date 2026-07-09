from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN", ""))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_USERNAME = str(os.getenv("CHANNEL_USERNAME", ""))

RAW_DATABASE_URL = str(os.getenv("DATABASE_URL", ""))
if RAW_DATABASE_URL.startswith("postgres://"):
    RAW_DATABASE_URL = RAW_DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif RAW_DATABASE_URL.startswith("postgresql://"):
    RAW_DATABASE_URL = RAW_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

DATABASE_URL = RAW_DATABASE_URL or "sqlite+aiosqlite:///database.db"