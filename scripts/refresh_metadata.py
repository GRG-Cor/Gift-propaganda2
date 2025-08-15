#!/usr/bin/env python3
"""
Скрипт для принудительного обновления метаданных SQLAlchemy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.db import engine, Base
from sqlalchemy import text

def refresh_metadata():
    """Принудительно обновляет метаданные SQLAlchemy"""
    try:
        with engine.connect() as conn:
            # Принудительно обновляем метаданные
            conn.execute(text("SELECT 1"))
            
            # Проверяем, что таблица существует и имеет нужные колонки
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'news_items' 
                AND column_name = 'content_html'
            """))
            
            if result.fetchone():
                print("✅ Колонка content_html найдена в базе данных")
                
                # Принудительно обновляем метаданные SQLAlchemy
                Base.metadata.reflect(bind=engine)
                print("✅ Метаданные SQLAlchemy обновлены")
                
                # Проверяем модель
                from server.db import NewsItem
                if hasattr(NewsItem, 'content_html'):
                    print("✅ Модель NewsItem содержит content_html")
                else:
                    print("❌ Модель NewsItem НЕ содержит content_html")
            else:
                print("❌ Колонка content_html НЕ найдена в базе данных")

    except Exception as e:
        print(f"Ошибка при обновлении метаданных: {e}")

if __name__ == "__main__":
    refresh_metadata() 