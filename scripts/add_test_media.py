#!/usr/bin/env python3
"""
Скрипт для добавления тестовых новостей с медиа контентом
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.db import SessionLocal, NewsItem, NewsSource
from datetime import datetime
import json

def add_test_news_with_media():
    """Добавляет тестовые новости с медиа контентом"""
    db = SessionLocal()
    
    try:
        # Создаем тестовый источник
        test_source = db.query(NewsSource).filter(NewsSource.name == "Test Media Source").first()
        if not test_source:
            test_source = NewsSource(
                name="Test Media Source",
                url="https://t.me/test_media_source",
                source_type="telegram",
                category="gifts",
                is_active=True
            )
            db.add(test_source)
            db.flush()
        
        # Тестовые новости с медиа
        test_news = [
            {
                "title": "🎁 Тестовая новость с фото - Бесплатные подарки!",
                "content": "Это тестовая новость с изображением для проверки отображения медиа контента в приложении.",
                "content_html": "Это тестовая новость с изображением для проверки отображения медиа контента в приложении.<br><img src='https://picsum.photos/800/400?random=1' style='max-width:100%; height:auto; border-radius:8px; margin:10px 0;'/>",
                "link": "https://t.me/test_media_source/1",
                "category": "gifts",
                "media": [
                    {
                        "type": "photo",
                        "url": "https://picsum.photos/800/400?random=1",
                        "thumbnail": "https://picsum.photos/400/200?random=1",
                        "width": 800,
                        "height": 400
                    }
                ]
            },
            {
                "title": "📹 Тестовая новость с видео - Новые технологии",
                "content": "Тестовая новость с видео контентом для проверки воспроизведения видео в приложении.",
                "content_html": "Тестовая новость с видео контентом для проверки воспроизведения видео в приложении.<br><video controls poster='https://picsum.photos/800/450?random=2' style='max-width:100%; height:auto; border-radius:8px; margin:10px 0;'><source src='https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4' type='video/mp4'></video>",
                "link": "https://t.me/test_media_source/2",
                "category": "tech",
                "media": [
                    {
                        "type": "video",
                        "url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
                        "thumbnail": "https://picsum.photos/800/450?random=2",
                        "width": 1280,
                        "height": 720
                    }
                ]
            },
            {
                "title": "🖼️ Тестовая новость с несколькими фото - NFT коллекция",
                "content": "Тестовая новость с несколькими изображениями для проверки отображения галереи.",
                "content_html": "Тестовая новость с несколькими изображениями для проверки отображения галереи.<br><img src='https://picsum.photos/800/400?random=3' style='max-width:100%; height:auto; border-radius:8px; margin:10px 0;'/><br><img src='https://picsum.photos/800/400?random=4' style='max-width:100%; height:auto; border-radius:8px; margin:10px 0;'/>",
                "link": "https://t.me/test_media_source/3",
                "category": "nft",
                "media": [
                    {
                        "type": "photo",
                        "url": "https://picsum.photos/800/400?random=3",
                        "thumbnail": "https://picsum.photos/400/200?random=3",
                        "width": 800,
                        "height": 400
                    },
                    {
                        "type": "photo",
                        "url": "https://picsum.photos/800/400?random=4",
                        "thumbnail": "https://picsum.photos/400/200?random=4",
                        "width": 800,
                        "height": 400
                    }
                ]
            },
            {
                "title": "₿ Тестовая новость без медиа - Крипто новости",
                "content": "Это тестовая новость без медиа контента для проверки корректного отображения текстовых новостей.",
                "content_html": "Это тестовая новость без медиа контента для проверки корректного отображения текстовых новостей.",
                "link": "https://t.me/test_media_source/4",
                "category": "crypto",
                "media": []
            }
        ]
        
        # Добавляем тестовые новости
        for i, news_data in enumerate(test_news):
            # Проверяем, существует ли уже такая новость
            existing = db.query(NewsItem).filter(
                NewsItem.title == news_data["title"],
                NewsItem.source_id == test_source.id
            ).first()
            
            if not existing:
                news_item = NewsItem(
                    source_id=test_source.id,
                    title=news_data["title"],
                    content=news_data["content"],
                    content_html=news_data["content_html"],
                    link=news_data["link"],
                    publish_date=datetime.now(),
                    category=news_data["category"],
                    media=news_data["media"],
                    reading_time=2,
                    views_count=0,
                    author="Test Author"
                )
                db.add(news_item)
                print(f"Добавлена тестовая новость: {news_data['title']}")
            else:
                print(f"Новость уже существует: {news_data['title']}")
        
        db.commit()
        print("Тестовые новости с медиа успешно добавлены!")
        
    except Exception as e:
        print(f"Ошибка при добавлении тестовых новостей: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_news_with_media() 