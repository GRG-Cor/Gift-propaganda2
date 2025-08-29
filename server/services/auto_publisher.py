"""
Сервис для автоматической публикации новостей в Telegram канал
"""
import asyncio
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from db import get_db_session, NewsItem, NewsSource
from config import (
    TOKEN, CHANNEL_ID, AUTO_PUBLISH_ENABLED, AUTO_PUBLISH_INTERVAL,
    AUTO_PUBLISH_LIMIT, POST_SIGNATURE, SOURCE_LINK_TEXT
)

logger = logging.getLogger(__name__)


class AutoPublisher:
    """Сервис для автоматической публикации новостей в Telegram канал"""
    
    def __init__(self):
        self.token = TOKEN
        self.channel_id = CHANNEL_ID
        self.enabled = AUTO_PUBLISH_ENABLED
        self.interval = AUTO_PUBLISH_INTERVAL
        self.limit = AUTO_PUBLISH_LIMIT
        self.signature = POST_SIGNATURE
        self.source_link_text = SOURCE_LINK_TEXT
        
        if not self.token:
            logger.error("Telegram bot token not configured!")
            self.enabled = False
            
        if not self.channel_id:
            logger.error("Channel ID not configured!")
            self.enabled = False
    
    def clean_text_for_telegram(self, text: str) -> str:
        """
        Очищает текст от символов, которые могут вызвать проблемы с Markdown
        """
        import re
        
        # Экранируем специальные символы Markdown
        text = re.sub(r'([*_`\[\]()~>#+=|{}.!-])', r'\\\1', text)
        
        # Убираем множественные обратные слеши
        text = re.sub(r'\\{2,}', r'\\', text)
        
        return text
    
    def format_post_content(self, news_item: NewsItem, source: Optional[NewsSource] = None) -> str:
        """
        Форматирует контент поста для публикации в Telegram канал
        """
        # Основной контент
        content_parts = []
        
        # Заголовок
        content_parts.append(f"📰 <b>{self.clean_text_for_telegram(news_item.title)}</b>")
        content_parts.append("")
        
        # Краткое описание (первые 300 символов)
        description = news_item.content[:300]
        if len(news_item.content) > 300:
            description += "..."
        content_parts.append(self.clean_text_for_telegram(description))
        content_parts.append("")
        
        # Категория
        category_emoji = {
            'gifts': '🎁',
            'crypto': '💰',
            'nft': '🖼️',
            'tech': '💻',
            'community': '👥',
            'general': '📢'
        }
        emoji = category_emoji.get(news_item.category, '📢')
        content_parts.append(f"{emoji} Категория: {news_item.category}")
        
        # Автор/источник
        if news_item.author:
            content_parts.append(f"👤 Автор: {self.clean_text_for_telegram(news_item.author)}")
        
        # Время чтения
        if news_item.reading_time:
            content_parts.append(f"⏱️ Время чтения: {news_item.reading_time} мин")
        
        # Просмотры
        if news_item.views_count:
            content_parts.append(f"👀 Просмотров: {news_item.views_count}")
        
        content_parts.append("")
        
        # Подпись и ссылка на источник
        content_parts.append(f"---")
        content_parts.append(f"{self.clean_text_for_telegram(self.signature)}")
        content_parts.append("")
        content_parts.append(f"{self.source_link_text}: {news_item.link}")
        
        return "\n".join(content_parts)
    
    def get_media_data(self, news_item: NewsItem) -> Optional[Dict[str, Any]]:
        """
        Извлекает медиа данные для публикации
        """
        # Приоритет: media JSON > image_url > video_url
        if news_item.media:
            try:
                if isinstance(news_item.media, str):
                    import json
                    media_data = json.loads(news_item.media)
                else:
                    media_data = news_item.media
                
                # Если это список медиа, берем первое
                if isinstance(media_data, list) and media_data:
                    media_data = media_data[0]
                
                if media_data.get('type') == 'photo' and media_data.get('url'):
                    return {
                        'type': 'photo',
                        'url': media_data['url']
                    }
                elif media_data.get('type') == 'video' and media_data.get('url'):
                    return {
                        'type': 'video',
                        'url': media_data['url']
                    }
            except Exception as e:
                logger.warning(f"Error parsing media for news {news_item.id}: {e}")
        
        # Fallback к image_url или video_url
        if news_item.image_url:
            return {
                'type': 'photo',
                'url': news_item.image_url
            }
        elif news_item.video_url:
            return {
                'type': 'video',
                'url': news_item.video_url
            }
        
        return None
    
    async def publish_news_to_channel(self, news_item: NewsItem) -> Optional[int]:
        """
        Публикует новость в Telegram канал
        Возвращает ID сообщения в канале или None при ошибке
        """
        try:
            # Получаем источник
            db = get_db_session()
            source = db.query(NewsSource).filter(NewsSource.id == news_item.source_id).first()
            
            # Форматируем контент
            content = self.format_post_content(news_item, source)
            
            # Получаем медиа
            media_data = self.get_media_data(news_item)
            
            # Публикуем в канал
            if media_data and media_data['type'] == 'photo':
                # Публикация с фото
                response = requests.post(
                    f"https://api.telegram.org/bot{self.token}/sendPhoto",
                    data={
                        'chat_id': self.channel_id,
                        'photo': media_data['url'],
                        'caption': content,
                        'parse_mode': 'HTML'
                    },
                    timeout=30
                )
            elif media_data and media_data['type'] == 'video':
                # Публикация с видео
                response = requests.post(
                    f"https://api.telegram.org/bot{self.token}/sendVideo",
                    data={
                        'chat_id': self.channel_id,
                        'video': media_data['url'],
                        'caption': content,
                        'parse_mode': 'HTML'
                    },
                    timeout=30
                )
            else:
                # Публикация только текста
                response = requests.post(
                    f"https://api.telegram.org/bot{self.token}/sendMessage",
                    data={
                        'chat_id': self.channel_id,
                        'text': content,
                        'parse_mode': 'HTML',
                        'disable_web_page_preview': False
                    },
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    message_id = result['result']['message_id']
                    logger.info(f"Successfully published news {news_item.id} to channel, message_id: {message_id}")
                    
                    # Обновляем статус в базе данных
                    news_item.is_published_to_channel = True
                    news_item.published_to_channel_at = datetime.utcnow()
                    news_item.telegram_message_id = message_id
                    db.commit()
                    
                    return message_id
                else:
                    logger.error(f"Telegram API error: {result}")
                    return None
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error publishing news {news_item.id} to channel: {e}")
            return None
        finally:
            if 'db' in locals():
                db.close()
    
    def get_unpublished_news(self, limit: int = None) -> List[NewsItem]:
        """
        Получает неопубликованные новости для публикации
        """
        try:
            db = get_db_session()
            
            # Получаем свежие неопубликованные новости
            query = db.query(NewsItem).filter(
                NewsItem.is_published_to_channel == False
            ).order_by(desc(NewsItem.publish_date))
            
            if limit:
                query = query.limit(limit)
            
            news_items = query.all()
            logger.info(f"Found {len(news_items)} unpublished news items")
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error getting unpublished news: {e}")
            return []
        finally:
            if 'db' in locals():
                db.close()
    
    async def publish_batch(self, force: bool = False) -> int:
        """
        Публикует пакет новостей в канал
        force: если True, публикует независимо от AUTO_PUBLISH_ENABLED (для ручной публикации)
        Возвращает количество опубликованных новостей
        """
        if not self.enabled and not force:
            logger.info("Auto publishing is disabled")
            return 0
        
        try:
            # Получаем неопубликованные новости
            news_items = self.get_unpublished_news(self.limit)
            
            if not news_items:
                logger.info("No unpublished news to publish")
                return 0
            
            published_count = 0
            
            # Публикуем каждую новость с задержкой
            for news_item in news_items:
                try:
                    message_id = await self.publish_news_to_channel(news_item)
                    if message_id:
                        published_count += 1
                        logger.info(f"Published news {news_item.id} (message_id: {message_id})")
                    
                    # Задержка между публикациями (чтобы не спамить)
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Error publishing news {news_item.id}: {e}")
                    continue
            
            logger.info(f"Published {published_count} news items to channel")
            return published_count
            
        except Exception as e:
            logger.error(f"Error in publish_batch: {e}")
            return 0
    
    async def start_auto_publishing(self):
        """
        Запускает автоматическую публикацию в фоновом режиме
        """
        if not self.enabled:
            logger.info("Auto publishing is disabled, not starting")
            return
        
        logger.info(f"Starting auto publishing service (interval: {self.interval}s)")
        
        while True:
            try:
                await self.publish_batch()
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error in auto publishing loop: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повторной попыткой


# Глобальный экземпляр сервиса
auto_publisher = AutoPublisher()
