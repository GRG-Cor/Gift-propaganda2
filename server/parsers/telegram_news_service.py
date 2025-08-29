#!/usr/bin/env python3
"""
Сервис для парсинга новостей из Telegram каналов
"""

import asyncio
import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from db import get_db_session, NewsItem, NewsSource
from config import TOKEN

logger = logging.getLogger(__name__)

class TelegramNewsService:
    def __init__(self):
        self.token = TOKEN
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_telegram_channels(self) -> List[Dict[str, Any]]:
        """Получение списка Telegram каналов из базы данных"""
        try:
            db = get_db_session()
            channels = db.query(NewsSource).filter(
                NewsSource.source_type == 'telegram',
                NewsSource.is_active == True
            ).all()
            
            return [
                {
                    'id': channel.id,
                    'name': channel.name,
                    'url': channel.url,
                    'category': channel.category
                }
                for channel in channels
            ]
        except Exception as e:
            logger.error(f"Ошибка при загрузке каналов: {e}")
            return []
        finally:
            if 'db' in locals():
                db.close()
    
    def get_rss_sources(self) -> List[Dict[str, Any]]:
        """Получение списка RSS источников из базы данных"""
        try:
            db = get_db_session()
            sources = db.query(NewsSource).filter(
                NewsSource.source_type == 'rss',
                NewsSource.is_active == True
            ).all()
            
            return [
                {
                    'id': source.id,
                    'name': source.name,
                    'url': source.url,
                    'category': source.category
                }
                for source in sources
            ]
        except Exception as e:
            logger.error(f"Ошибка при загрузке RSS источников: {e}")
            return []
        finally:
            if 'db' in locals():
                db.close()
    
    async def fetch_telegram_channel(self, channel_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Получение постов из Telegram канала"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            # Убираем @ если есть
            channel_name = channel_name.lstrip('@')
            
            # URL для получения постов
            url = f"https://t.me/s/{channel_name}"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Ошибка получения канала {channel_name}: {response.status}")
                    return []
                
                html = await response.text()
                
            # Парсим HTML
            soup = BeautifulSoup(html, 'html.parser')
            posts = []
            
            # Ищем все посты
            message_elements = soup.find_all('div', class_='tgme_widget_message')
            
            for element in message_elements[:limit]:
                try:
                    # Извлекаем данные поста
                    post_data = self._parse_telegram_post(element, channel_name)
                    if post_data:
                        posts.append(post_data)
                except Exception as e:
                    logger.error(f"Ошибка парсинга поста: {e}")
                    continue
            
            logger.info(f"Got {len(posts)} posts from {channel_name}")
            return posts
            
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при получении канала {channel_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Ошибка получения канала {channel_name}: {e}")
            return []
    
    def _parse_telegram_post(self, element, channel_name: str) -> Optional[Dict[str, Any]]:
        """Парсинг отдельного поста из Telegram"""
        try:
            # Получаем текст поста
            text_element = element.find('div', class_='tgme_widget_message_text')
            if not text_element:
                return None
            
            text = text_element.get_text(strip=True)
            if not text:
                return None
            
            # Получаем дату
            date_element = element.find('time')
            if date_element:
                date_str = date_element.get('datetime')
                if date_str:
                    try:
                        publish_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        publish_date = datetime.now()
                else:
                    publish_date = datetime.now()
            else:
                publish_date = datetime.now()
            
            # Получаем ссылку на пост
            link_element = element.find('a', class_='tgme_widget_message_date')
            link = None
            if link_element:
                link = link_element.get('href')
            
            # Получаем медиа
            media_data = self._extract_media(element)
            
            # Определяем категорию
            category = self._categorize_content(text)
            
            return {
                'title': text[:200] + '...' if len(text) > 200 else text,
                'content': text,
                'content_html': text,
                'link': link or f"https://t.me/{channel_name}",
                'publish_date': publish_date,
                'category': category,
                'author': channel_name,
                'source_name': channel_name,
                'media': media_data
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга поста: {e}")
            return None
    
    def _extract_media(self, element) -> List[Dict[str, Any]]:
        """Извлечение медиа из поста"""
        media = []
        
        try:
            # Ищем фото
            photos = element.find_all('a', class_='tgme_widget_message_photo_wrap')
            for photo in photos:
                photo_url = photo.get('style')
                if photo_url:
                    # Извлекаем URL из style
                    match = re.search(r'background-image:url\(([^)]+)\)', photo_url)
                    if match:
                        url = match.group(1)
                        logger.info(f"Found photo: {url}")
                        media.append({
                            'type': 'photo',
                            'url': url
                        })
            
            # Ищем видео
            videos = element.find_all('video')
            for video in videos:
                video_url = video.get('src')
                if video_url:
                    logger.info(f"Found video: {video_url}")
                    media.append({
                        'type': 'video',
                        'url': video_url
                    })
            
        except Exception as e:
            logger.error(f"Ошибка извлечения медиа: {e}")
        
        return media
    
    def _categorize_content(self, text: str) -> str:
        """Категоризация контента"""
        text_lower = text.lower()
        
        # Ключевые слова для категорий
        categories = {
            'gifts': ['подарок', 'подарки', 'акция', 'скидка', 'промокод', 'бесплатно', 'giveaway', 'airdrop'],
            'crypto': ['биткоин', 'крипто', 'блокчейн', 'bitcoin', 'ethereum', 'crypto', 'blockchain', 'defi', 'nft'],
            'nft': ['nft', 'токен', 'коллекция', 'токенизация', 'non-fungible'],
            'tech': ['технологии', 'ai', 'искусственный интеллект', 'машинное обучение', 'startup', 'инновации'],
            'community': ['сообщество', 'мероприятие', 'встреча', 'конференция', 'хакатон']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'general'
    
    async def fetch_rss_feed(self, feed_url: str, source_name: str, category: str = None) -> List[Dict[str, Any]]:
        """Получение новостей из RSS ленты"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(feed_url) as response:
                if response.status != 200:
                    logger.error(f"Ошибка получения RSS {feed_url}: {response.status}")
                    return []
                
                content = await response.text()
            
            # Парсим RSS
            feed = feedparser.parse(content)
            articles = []
            
            for entry in feed.entries[:10]:  # Берем последние 10 статей
                try:
                    # Очищаем текст от HTML тегов
                    if hasattr(entry, 'summary'):
                        summary = BeautifulSoup(entry.summary, 'html.parser').get_text()
                    else:
                        summary = entry.title
                    
                    # Ограничиваем длину
                    if len(summary) > 300:
                        summary = summary[:300] + '...'
                    
                    # Определяем категорию
                    article_category = category or self._categorize_content(entry.title + ' ' + summary)
                    
                    # Получаем дату
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        publish_date = datetime(*entry.published_parsed[:6])
                    else:
                        publish_date = datetime.now()
                    
                    articles.append({
                        'title': entry.title,
                        'content': summary,
                        'content_html': summary,
                        'link': entry.link,
                        'publish_date': publish_date,
                        'category': article_category,
                        'author': getattr(entry, 'author', source_name),
                        'source_name': source_name,
                        'media': []
                    })
                    
                except Exception as e:
                    logger.error(f"Ошибка парсинга RSS статьи: {e}")
                    continue
            
            logger.info(f"Got {len(articles)} articles from {source_name}")
            return articles
            
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при получении RSS {feed_url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Ошибка получения RSS {feed_url}: {e}")
            return []
    
    def save_news_items(self, news_items: List[Dict[str, Any]]) -> int:
        """Сохранение новостей в базу данных"""
        try:
            db = get_db_session()
            saved_count = 0
            
            for item in news_items:
                try:
                    # Проверяем, есть ли уже такая новость
                    existing = db.query(NewsItem).filter(
                        NewsItem.title == item['title']
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Получаем или создаем источник
                    source = db.query(NewsSource).filter(
                        NewsSource.name == item['source_name']
                    ).first()
                    
                    if not source:
                        source = NewsSource(
                            name=item['source_name'],
                            url=item.get('link', ''),
                            source_type='telegram' if '@' in item['source_name'] else 'rss',
                            category=item['category'],
                            is_active=True
                        )
                        db.add(source)
                        db.flush()  # Получаем ID
                    
                    # Создаем новость
                    news_item = NewsItem(
                        title=item['title'],
                        content=item['content'],
                        content_html=item.get('content_html', item['content']),
                        link=item['link'],
                        publish_date=item['publish_date'],
                        category=item['category'],
                        author=item.get('author', ''),
                        source_id=source.id,
                        image_url=item.get('media', [{}])[0].get('url') if item.get('media') else None,
                        video_url=None,  # Можно добавить логику для видео
                        reading_time=len(item['content']) // 200,  # Примерное время чтения
                        views_count=0,
                        is_published_to_channel=False
                    )
                    
                    db.add(news_item)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Ошибка сохранения новости: {e}")
                    continue
            
            db.commit()
            logger.info(f"Successfully updated {saved_count} news items")
            return saved_count
            
        except Exception as e:
            logger.error(f"Ошибка сохранения новостей: {e}")
            if 'db' in locals():
                db.rollback()
            return 0
        finally:
            if 'db' in locals():
                db.close()
    
    async def update_all_news(self):
        """Обновление всех новостей"""
        try:
            # Получаем Telegram каналы
            telegram_channels = self.get_telegram_channels()
            logger.info(f"Fetching from {len(telegram_channels)} Telegram channels")
            
            all_posts = []
            
            # Получаем посты из Telegram каналов
            for channel in telegram_channels:
                channel_name = channel['name'].replace('@', '')
                posts = await self.fetch_telegram_channel(channel_name, 20)
                all_posts.extend(posts)
            
            # Получаем RSS источники
            rss_sources = self.get_rss_sources()
            logger.info(f"Fetching from {len(rss_sources)} RSS sources")
            
            # Получаем статьи из RSS
            for source in rss_sources:
                articles = await self.fetch_rss_feed(source['url'], source['name'], source['category'])
                all_posts.extend(articles)
            
            # Убираем дубликаты
            unique_posts = self._deduplicate_posts(all_posts)
            logger.info(f"After deduplication: {len(unique_posts)} unique posts from {len(all_posts)} total")
            
            # Сохраняем в базу
            saved_count = self.save_news_items(unique_posts)
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Ошибка обновления новостей: {e}")
            return 0
    
    def _deduplicate_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Удаление дубликатов постов"""
        seen_titles = set()
        unique_posts = []
        
        for post in posts:
            # Нормализуем заголовок для сравнения
            title_key = post['title'].lower().strip()
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_posts.append(post)
        
        return unique_posts

# Создаем экземпляр сервиса
telegram_service = TelegramNewsService()
