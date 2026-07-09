from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN", ""))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_USERNAME = str(os.getenv("CHANNEL_USERNAME", ""))
DATABASE_URL = str(os.getenv("DATABASE_URL", "sqlite+aiosqlite:///database.db"))