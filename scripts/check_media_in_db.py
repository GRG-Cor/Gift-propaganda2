#!/usr/bin/env python3
"""
Скрипт для проверки медиа в базе данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.db import SessionLocal, NewsItem
import json

def check_media_in_database():
    """Проверяем медиа в базе данных"""
    print("🔍 Проверка медиа в базе данных...")
    
    db = SessionLocal()
    try:
        # Получаем все новости с медиа
        news_with_media = db.query(NewsItem).filter(NewsItem.media.isnot(None)).limit(10).all()
        
        print(f"📊 Найдено новостей с медиа: {len(news_with_media)}")
        
        for i, news in enumerate(news_with_media[:5]):  # Показываем первые 5
            print(f"\n📰 Новость {i+1}: {news.title[:50]}...")
            print(f"   ID: {news.id}")
            print(f"   Категория: {news.category}")
            print(f"   Источник: {news.author}")
            
            if news.media:
                print(f"   📷 Медиа: {json.dumps(news.media, indent=2, ensure_ascii=False)}")
            else:
                print("   ❌ Медиа отсутствует")
                
            if news.image_url:
                print(f"   🖼️ Image URL: {news.image_url}")
            if news.video_url:
                print(f"   🎬 Video URL: {news.video_url}")
        
        # Проверяем общее количество новостей
        total_news = db.query(NewsItem).count()
        news_with_media_count = db.query(NewsItem).filter(NewsItem.media.isnot(None)).count()
        
        print(f"\n📈 Статистика:")
        print(f"   Всего новостей: {total_news}")
        print(f"   С медиа: {news_with_media_count}")
        print(f"   Процент с медиа: {(news_with_media_count/total_news*100):.1f}%")
        
        # Проверяем по категориям
        categories = db.query(NewsItem.category).distinct().all()
        for category in categories:
            cat = category[0]
            if cat:
                total_in_cat = db.query(NewsItem).filter(NewsItem.category == cat).count()
                with_media_in_cat = db.query(NewsItem).filter(
                    NewsItem.category == cat,
                    NewsItem.media.isnot(None)
                ).count()
                print(f"   {cat.upper()}: {with_media_in_cat}/{total_in_cat} ({with_media_in_cat/total_in_cat*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_media_in_database() 