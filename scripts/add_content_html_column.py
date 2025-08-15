#!/usr/bin/env python3
"""
Скрипт для добавления колонки content_html в таблицу news_items
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.db import engine
from sqlalchemy import text

def add_content_html_column():
    """Добавляет колонку content_html в таблицу news_items"""
    try:
        with engine.connect() as conn:
            # Проверяем, существует ли уже колонка
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'news_items' 
                AND column_name = 'content_html'
            """))
            
            if result.fetchone():
                print("Колонка content_html уже существует")
                return
            
            # Добавляем колонку
            conn.execute(text("""
                ALTER TABLE news_items 
                ADD COLUMN content_html TEXT
            """))
            
            conn.commit()
            print("Колонка content_html успешно добавлена!")
            
    except Exception as e:
        print(f"Ошибка при добавлении колонки: {e}")

if __name__ == "__main__":
    add_content_html_column() 