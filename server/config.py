from dotenv import load_dotenv
import os

load_dotenv()

# Настройки базы данных - для Render
# Получаем DATABASE_URL из переменных окружения или используем SQLite для локальной разработки
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./news.db")

# Настройки Telegram Bot
TOKEN = os.getenv("TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN", "8429342375:AAFl55U3d2jiq3bm4UNTyDrbB0rztFTio2I")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://c614d13bcb7d.ngrok-free.app")

# Настройки Redis (если используется)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Другие настройки
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Логирование для отладки
print(f"DATABASE_URL: {DATABASE_URL[:50]}...")
print(f"TOKEN: {'SET' if TOKEN else 'NOT SET'}")
print(f"WEBHOOK_URL: {WEBHOOK_URL}")
