#!/usr/bin/env python3
"""
Скрипт для проверки структуры таблицы news_items
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.db import engine
from sqlalchemy import text

def check_table_structure():
    """Проверяет структуру таблицы news_items"""
    try:
        with engine.connect() as conn:
            # Получаем список всех колонок в таблице
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'news_items'
                ORDER BY ordinal_position
            """))

            print("Структура таблицы news_items:")
            print("-" * 50)
            for row in result:
                print(f"{row[0]:<20} {row[1]:<15} {row[2]}")
            
            # Проверяем конкретно content_html
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'news_items'
                AND column_name = 'content_html'
            """))

            if result.fetchone():
                print("\n✅ Колонка content_html существует")
            else:
                print("\n❌ Колонка content_html НЕ существует")

    except Exception as e:
        print(f"Ошибка при проверке структуры: {e}")

if __name__ == "__main__":
    check_table_structure() 