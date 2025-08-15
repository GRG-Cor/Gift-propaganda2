#!/usr/bin/env python3
"""
Принудительное обновление новостей с медиа
"""

import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))
from server.parsers.telegram_news_service import TelegramNewsService

async def force_update():
    """Принудительное обновление новостей"""
    print("🔄 Принудительное обновление новостей...")
    
    try:
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
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(force_update()) 