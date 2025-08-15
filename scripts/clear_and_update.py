#!/usr/bin/env python3
"""
Очистка базы данных и обновление с медиа
"""

import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))
from server.db import get_db_session, NewsItem, NewsSource

async def clear_and_update():
    """Очистка базы данных и обновление с медиа"""
    print("🗑️ Очистка базы данных...")
    
    try:
        with get_db_session() as session:
            # Удаляем все новости от NextGen NFT
            nextgen_news = session.query(NewsItem).join(NewsItem.source).filter(
                NewsItem.source.has(name="NextGen NFT")
            ).all()
            
            deleted_count = len(nextgen_news)
            for item in nextgen_news:
                session.delete(item)
            
            session.commit()
            print(f"✅ Удалено {deleted_count} новостей от NextGen NFT")
        
        print("🔄 Обновление новостей с медиа...")
        
        # Импортируем сервис
        from server.parsers.telegram_news_service import TelegramNewsService
        service = TelegramNewsService()
        
        # Получаем посты из канала
        print("📡 Получение постов из @nextgen_NFT...")
        posts = await service.fetch_telegram_channel('nextgen_NFT')
        
        print(f"✅ Получено {len(posts)} постов")
        
        # Проверяем медиа
        media_posts = []
        for i, post in enumerate(posts):
            if post.get('media'):
                media_posts.append((i+1, post))
                print(f"📸 Пост #{i+1}: {post['media']}")
        
        print(f"📊 Постов с медиа: {len(media_posts)}")
        
        # Сохраняем в базу данных
        print("💾 Сохранение в базу данных...")
        await service.save_to_database(posts)
        
        print("✅ Обновление завершено!")
        
        # Проверяем результат
        print("🔍 Проверка результата...")
        with get_db_session() as session:
            nextgen_news = session.query(NewsItem).join(NewsItem.source).filter(
                NewsItem.source.has(name="NextGen NFT")
            ).all()
            
            print(f"📊 Всего новостей от NextGen NFT: {len(nextgen_news)}")
            
            media_count = 0
            for item in nextgen_news:
                if item.media:
                    media_count += 1
                    print(f"   ✅ ID {item.id}: {len(item.media)} медиа элементов")
            
            print(f"📸 Новостей с медиа: {media_count}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(clear_and_update()) 