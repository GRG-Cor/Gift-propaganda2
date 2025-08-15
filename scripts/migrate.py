#!/usr/bin/env python3
"""
Скрипт для применения миграций базы данных
"""
import os
import sys
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import logging

# Добавляем путь к серверу для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from server.config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def apply_migration():
    """Применяет миграцию для добавления новых полей"""

    # Заменяем postgresql:// на postgresql+asyncpg://
    async_url = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
    engine = create_async_engine(async_url)

    try:
        async with engine.begin() as conn:
            logger.info("Подключение к базе данных...")

            # Проверяем, существуют ли уже поля
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'news_items' 
                AND column_name IN ('image_url', 'video_url', 'reading_time', 'views_count', 'author', 'subtitle', 'content_html')
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
                ('content_html', 'TEXT')
            ]

            for field_name, field_type in fields_to_add:
                if field_name not in existing_columns:
                    logger.info(f"Добавляем поле {field_name}...")
                    await conn.execute(text(f"""
                        ALTER TABLE news_items 
                        ADD COLUMN {field_name} {field_type}
                    """))
                    logger.info(f"Поле {field_name} добавлено успешно")
                else:
                    logger.info(f"Поле {field_name} уже существует")

            logger.info("Миграция применена успешно!")

    except Exception as e:
        logger.error(f"Ошибка при применении миграции: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(apply_migration())
