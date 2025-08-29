from dotenv import load_dotenv
import os

load_dotenv()

# Настройки базы данных - для Render
# Получаем DATABASE_URL из переменных окружения или используем SQLite для локальной разработки
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./news.db")

# Настройки Telegram Bot
TOKEN = os.getenv("TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN", "8429342375:AAFl55U3d2jiq3bm4UNTyDrbB0rztFTio2I")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://gift-propaganda-cf8i.onrender.com")

# Настройки для автоматической публикации постов в канал    
CHANNEL_ID = os.getenv("CHANNEL_ID", "@gift_propaganda_channel")  # ID канала для публикации
AUTO_PUBLISH_ENABLED = os.getenv("AUTO_PUBLISH_ENABLED", "false").lower() == "true"  # ОТКЛЮЧЕНО по умолчанию
AUTO_PUBLISH_INTERVAL = int(os.getenv("AUTO_PUBLISH_INTERVAL", "3600"))  # Интервал публикации в секундах (1 час)
AUTO_PUBLISH_LIMIT = int(os.getenv("AUTO_PUBLISH_LIMIT", "5"))  # Количество постов за раз

# Подпись для постов (будет добавляться в конец каждого поста)
POST_SIGNATURE = os.getenv("POST_SIGNATURE", "🎁 Gift Propaganda - Ваш источник лучших новостей!")
SOURCE_LINK_TEXT = os.getenv("SOURCE_LINK_TEXT", "📰 Читать источник")

# Настройки Redis (если используется)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Другие настройки
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Логирование для отладки
print(f"DATABASE_URL: {DATABASE_URL[:50]}...")
print(f"TOKEN: {'SET' if TOKEN else 'NOT SET'}")
print(f"WEBHOOK_URL: {WEBHOOK_URL}")
print(f"CHANNEL_ID: {CHANNEL_ID}")
print(f"AUTO_PUBLISH_ENABLED: {AUTO_PUBLISH_ENABLED} (ОТКЛЮЧЕНО - только ручная публикация)")
print(f"AUTO_PUBLISH_INTERVAL: {AUTO_PUBLISH_INTERVAL} seconds")
