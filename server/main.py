import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import time

# Исправленные импорты
from server.db import Base, NewsItem, NewsSource, engine, SessionLocal, create_tables, recreate_engine
from server.parsers.telegram_news_service import TelegramNewsService
from server.config import TOKEN, WEBHOOK_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных с повторными попытками"""
    # Проверяем переменные окружения
    database_url = os.getenv('DATABASE_URL', 'postgresql://news_db_bnnu_user:QkbkVviv0rOOKW2LIXh2tkelyDICRLXv@dpg-d22i993e5dus739mr8n0-a.oregon-postgres.render.com/news_db_bnnu')
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
    """Применяет миграции базы данных"""
    try:
        logger.info("Проверка и применение миграций...")

        with engine.connect() as connection:
            # Проверяем, существуют ли новые поля
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'news_items' 
                AND column_name IN (
                    'image_url', 'video_url', 'reading_time', 'views_count', 
                    'author', 'subtitle', 'created_at', 'updated_at', 'content_html'
                )
            """))

            existing_columns = [row[0] for row in result.fetchall()]
            logger.info(f"Существующие новые поля: {existing_columns}")

            # Добавляем поля, которых еще нет
            fields_to_add = [
                ('image_url', 'VARCHAR(1000)'),
                ('video_url', 'VARCHAR(1000)'),
                ('reading_time', 'INTEGER'),
                ('views_count', 'INTEGER'),
                ('author', 'VARCHAR(200)'),
                ('subtitle', 'VARCHAR(500)'),
                ('created_at', 'TIMESTAMP DEFAULT NOW()'),
                ('updated_at', 'TIMESTAMP DEFAULT NOW()'),
                ('content_html', 'TEXT')
            ]

            for field_name, field_type in fields_to_add:
                if field_name not in existing_columns:
                    logger.info(f"Добавляем поле {field_name}...")
                    connection.execute(text(f"""
                        ALTER TABLE news_items 
                        ADD COLUMN {field_name} {field_type}
                    """))
                    connection.commit()
                    logger.info(f"Поле {field_name} добавлено успешно")
                else:
                    logger.info(f"Поле {field_name} уже существует")

            logger.info("Миграции применены успешно!")

    except Exception as e:
        logger.error(f"Ошибка при применении миграций: {e}")
        # Не прерываем запуск приложения из-за ошибки миграции
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения...")

    # Инициализация базы данных
    init_db()

    # Применение миграций
    apply_migrations()

    # Настройка webhook
    try:
        import requests
        webhook_response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            json={"url": f"{WEBHOOK_URL}/webhook"}
        )
        if webhook_response.status_code == 200:
            logger.info("Webhook установлен успешно")
        else:
            logger.warning(f"Ошибка установки webhook: {webhook_response.text}")
    except Exception as e:
        logger.error(f"Ошибка при установке webhook: {e}")

    # Запуск периодических задач
    news_service = TelegramNewsService()

    async def periodic_update():
        while True:
            try:
                await news_service.update_news_async()
                logger.info("Периодическое обновление завершено")
            except Exception as e:
                logger.error(f"Ошибка при обновлении новостей: {e}")
            await asyncio.sleep(300)  # обновляем каждые 5 минут

    asyncio.create_task(periodic_update())

    yield

    # Shutdown
    logger.info("Приложение завершает работу")

# Создаем FastAPI приложение
app = FastAPI(
    title="Gift Propaganda News API",
    description="API для агрегации новостей Telegram",
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
from server.api.news import router as news_router
from server.api.telegram import router as telegram_router

app.include_router(news_router, prefix="/api")
app.include_router(telegram_router, prefix="/telegram")

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