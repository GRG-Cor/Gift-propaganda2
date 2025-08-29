import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import time

# Исправленные импорты для локального запуска
from db import Base, NewsItem, NewsSource, engine, SessionLocal, create_tables, recreate_engine
from parsers.telegram_news_service import TelegramNewsService
from config import TOKEN, WEBHOOK_URL
from services.auto_publisher import auto_publisher  # Импортируем сервис автопубликации

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных с повторными попытками"""
    # Проверяем переменные окружения
    database_url = os.getenv('DATABASE_URL', 'postgresql://giftpropaganda_db_9f8b_user:1d49e4eYc6zLSzZ5yYl17CZJn7sgpUIV@dpg-d2fkuo2dbo4c73bd4vh0-a/giftpropaganda_db_9f8b')
    token = os.getenv('TOKEN')
    webhook_url = os.getenv('WEBHOOK_URL')

    # Обрезаем DATABASE_URL для логирования (убираем пароль)
    safe_db_url = database_url.replace('password', '***') if 'password' in database_url else database_url
    logger.info(f"DATABASE_URL: {safe_db_url}")
    logger.info(f"TOKEN: {'SET' if token else 'NOT SET'}")
    logger.info(f"WEBHOOK_URL: {webhook_url}")

    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            # Пересоздаем движок с обновленными метаданными
            global engine, SessionLocal
            engine = recreate_engine()
            
            # Проверяем подключение
            with engine.connect() as connection:
                logger.info("Успешное подключение к базе данных")

            # Создаем таблицы
            create_tables()

            logger.info("База данных инициализирована успешно")
            return

        except Exception as e:
            logger.warning(f"Попытка {attempt}/{max_attempts} подключения к базе: {e}")
            if attempt < max_attempts:
                time.sleep(5)
            continue

    raise Exception("Не удалось подключиться к базе данных после нескольких попыток")

def apply_migrations():
    """Применение миграций к базе данных"""
    try:
        logger.info("Проверка и применение миграций...")
        
        # Создаем таблицы если их нет
        Base.metadata.create_all(bind=engine)
        
        # Проверяем существование новых колонок для SQLite
        db = SessionLocal()
        try:
            # Проверяем существование колонки is_published_to_channel
            result = db.execute("PRAGMA table_info(news_items)")
            columns = [row[1] for row in result.fetchall()]
            
            # Добавляем новые колонки если их нет
            if 'is_published_to_channel' not in columns:
                db.execute("ALTER TABLE news_items ADD COLUMN is_published_to_channel BOOLEAN DEFAULT FALSE")
                logger.info("Добавлена колонка is_published_to_channel")
            
            if 'published_to_channel_at' not in columns:
                db.execute("ALTER TABLE news_items ADD COLUMN published_to_channel_at DATETIME")
                logger.info("Добавлена колонка published_to_channel_at")
            
            if 'telegram_message_id' not in columns:
                db.execute("ALTER TABLE news_items ADD COLUMN telegram_message_id INTEGER")
                logger.info("Добавлена колонка telegram_message_id")
            
            db.commit()
            logger.info("Миграции применены успешно")
            
        except Exception as e:
            logger.error(f"Ошибка при применении миграций: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка при применении миграций: {e}")

def init_news_sources():
    """Инициализация источников новостей"""
    try:
        db = SessionLocal()
        
        # Проверяем, есть ли уже источники
        existing_sources = db.query(NewsSource).count()
        if existing_sources > 0:
            logger.info(f"Найдено {existing_sources} источников новостей")
            return
        
        # Добавляем Telegram каналы
        telegram_sources = [
            {
                'name': '@nextgen_NFT',
                'url': 'https://t.me/nextgen_NFT',
                'source_type': 'telegram',
                'category': 'nft',
                'is_active': True
            }
        ]
        
        # Добавляем RSS источники
        rss_sources = [
            {
                'name': 'VC.ru',
                'url': 'https://vc.ru/rss',
                'source_type': 'rss',
                'category': 'tech',
                'is_active': True
            },
            {
                'name': 'CoinDesk',
                'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
                'source_type': 'rss',
                'category': 'crypto',
                'is_active': True
            },
            {
                'name': 'Cointelegraph',
                'url': 'https://cointelegraph.com/rss',
                'source_type': 'rss',
                'category': 'crypto',
                'is_active': True
            },
            {
                'name': 'Habr NFT',
                'url': 'https://habr.com/ru/rss/articles/',
                'source_type': 'rss',
                'category': 'nft',
                'is_active': True
            }
        ]
        
        # Добавляем все источники
        for source_data in telegram_sources + rss_sources:
            source = NewsSource(**source_data)
            db.add(source)
        
        db.commit()
        logger.info(f"Добавлено {len(telegram_sources + rss_sources)} источников новостей")
        
    except Exception as e:
        logger.error(f"Ошибка инициализации источников: {e}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения...")

    # Инициализация базы данных
    init_db()

    # Применение миграций
    apply_migrations()

    # Инициализация источников новостей
    init_news_sources()

    # Настройка webhook
    try:
        import requests
        webhook_response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            json={"url": f"{WEBHOOK_URL}/telegram/webhook"}
        )
        if webhook_response.status_code == 200:
            logger.info("Webhook установлен успешно")
        else:
            logger.warning(f"Ошибка установки webhook: {webhook_response.text}")
    except Exception as e:
        logger.error(f"Ошибка при установке webhook: {e}")

    # Запуск периодических задач
    news_service = TelegramNewsService()

    async def update_news():
        """Периодическое обновление новостей"""
        try:
            logger.info("Начинаем периодическое обновление новостей...")
            await news_service.update_all_news()
            logger.info("Периодическое обновление завершено")
        except Exception as e:
            logger.error(f"Ошибка при обновлении новостей: {e}")

    # Запускаем автоматическую публикацию в фоновом режиме
    async def auto_publishing_task():
        try:
            await auto_publisher.start_auto_publishing()
        except Exception as e:
            logger.error(f"Ошибка в задаче автопубликации: {e}")

    # Запускаем все фоновые задачи
    asyncio.create_task(update_news())
    asyncio.create_task(auto_publishing_task())

    yield

    # Shutdown
    logger.info("Приложение завершает работу")

# Создаем FastAPI приложение
app = FastAPI(
    title="Gift Propaganda News API",
    description="API для агрегации новостей Telegram с автоматической публикацией",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Импортируем роутеры после создания app
from api.news import router as news_router
from api.telegram import router as telegram_router

logger.info("Регистрируем роутеры...")
app.include_router(news_router, prefix="/api")
logger.info("✅ News router зарегистрирован")
app.include_router(telegram_router)
logger.info("✅ Telegram router зарегистрирован")
logger.info(f"Доступные роуты: {[route.path for route in app.routes]}")

@app.get("/")
async def root():
    return {"message": "Gift Propaganda News API", "status": "running"}

@app.get("/health")
async def health():
    try:
        # Проверяем подключение к БД
        with engine.connect() as connection:
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
