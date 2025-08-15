#!/usr/bin/env python3
"""
Скрипт для очистки старых новостей и оставления только новостей из канала @nextgen_NFT
"""

import sys
import os
from sqlalchemy import create_engine, text
from datetime import datetime

# Добавляем путь к серверу
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from server.config import DATABASE_URL

def clear_old_news():
    """Очищаем старые новости и оставляем только @nextgen_NFT"""
    
    print("🧹 Очистка старых новостей...")
    
    try:
        # Создаем подключение к базе данных
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            # Получаем информацию о количестве новостей
            result = connection.execute(text("SELECT COUNT(*) FROM news_items"))
            total_count = result.scalar()
            print(f"📊 Всего новостей в базе: {total_count}")
            
            # Получаем количество новостей от @nextgen_NFT
            result = connection.execute(text("""
                SELECT COUNT(*) FROM news_items ni 
                JOIN news_sources ns ON ni.source_id = ns.id 
                WHERE ns.name = 'NextGen NFT'
            """))
            nextgen_count = result.scalar()
            print(f"📊 Новостей от @nextgen_NFT: {nextgen_count}")
            
            # Удаляем все новости кроме @nextgen_NFT
            result = connection.execute(text("""
                DELETE FROM news_items 
                WHERE source_id NOT IN (
                    SELECT id FROM news_sources WHERE name = 'NextGen NFT'
                )
            """))
            deleted_count = result.rowcount
            print(f"🗑️ Удалено новостей: {deleted_count}")
            
            # Удаляем неиспользуемые источники
            result = connection.execute(text("""
                DELETE FROM news_sources 
                WHERE name != 'NextGen NFT'
            """))
            deleted_sources = result.rowcount
            print(f"🗑️ Удалено источников: {deleted_sources}")
            
            # Проверяем результат
            result = connection.execute(text("SELECT COUNT(*) FROM news_items"))
            final_count = result.scalar()
            print(f"✅ Осталось новостей: {final_count}")
            
            # Показываем оставшиеся новости
            result = connection.execute(text("""
                SELECT ni.title, ni.publish_date, ns.name 
                FROM news_items ni 
                JOIN news_sources ns ON ni.source_id = ns.id 
                ORDER BY ni.publish_date DESC 
                LIMIT 5
            """))
            
            print(f"\n📰 Последние новости:")
            for row in result:
                print(f"   • {row[0][:50]}... ({row[2]}) - {row[1]}")
            
            connection.commit()
            print(f"\n✅ Очистка завершена успешно!")
            
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clear_old_news() 