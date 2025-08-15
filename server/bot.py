#!/usr/bin/env python3
"""
Telegram Bot для Gift Propaganda News
"""

import logging
import requests
from typing import Dict, List, Optional
from server.config import TOKEN, WEBHOOK_URL
from server.db import get_db_session
from server.db import NewsItem, NewsSource
from sqlalchemy.orm import Session
from sqlalchemy import func

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """Отправка сообщения в Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False
    
    def send_photo(self, chat_id: int, photo_url: str, caption: str = "", parse_mode: str = "HTML") -> bool:
        """Отправка фото в Telegram"""
        try:
            url = f"{self.base_url}/sendPhoto"
            data = {
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка отправки фото: {e}")
            return False
    
    def send_media_group(self, chat_id: int, media: List[Dict]) -> bool:
        """Отправка группы медиа в Telegram"""
        try:
            url = f"{self.base_url}/sendMediaGroup"
            data = {
                "chat_id": chat_id,
                "media": media
            }
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка отправки медиа группы: {e}")
            return False
    
    def send_inline_keyboard(self, chat_id: int, text: str, keyboard: List[List[Dict]]) -> bool:
        """Отправка сообщения с inline клавиатурой"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "reply_markup": {
                    "inline_keyboard": keyboard
                }
            }
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка отправки клавиатуры: {e}")
            return False
    
    def get_news_summary(self, limit: int = 5) -> str:
        """Получение сводки новостей"""
        try:
            with get_db_session() as session:
                news_items = session.query(NewsItem).order_by(NewsItem.publish_date.desc()).limit(limit).all()
                
                if not news_items:
                    return "📰 Новостей пока нет"
                
                summary = f"📰 <b>Последние {len(news_items)} новостей:</b>\n\n"
                
                for i, news in enumerate(news_items, 1):
                    # Ограничиваем длину заголовка
                    title = news.title[:50] + "..." if len(news.title) > 50 else news.title
                    source = news.source.name if news.source else "Unknown"
                    category = news.category or "general"
                    
                    summary += f"{i}. <b>{title}</b>\n"
                    summary += f"   📍 {source} | #{category}\n"
                    summary += f"   📅 {news.publish_date.strftime('%d.%m.%Y %H:%M')}\n\n"
                
                return summary
        except Exception as e:
            logger.error(f"Ошибка получения сводки новостей: {e}")
            return "❌ Ошибка получения новостей"
    
    def get_news_by_category(self, category: str, limit: int = 5) -> str:
        """Получение новостей по категории"""
        try:
            with get_db_session() as session:
                news_items = session.query(NewsItem).filter(
                    NewsItem.category == category
                ).order_by(NewsItem.publish_date.desc()).limit(limit).all()
                
                if not news_items:
                    return f"📰 Новостей в категории #{category} пока нет"
                
                summary = f"📰 <b>Новости #{category}:</b>\n\n"
                
                for i, news in enumerate(news_items, 1):
                    title = news.title[:50] + "..." if len(news.title) > 50 else news.title
                    source = news.source.name if news.source else "Unknown"
                    
                    summary += f"{i}. <b>{title}</b>\n"
                    summary += f"   📍 {source}\n"
                    summary += f"   📅 {news.publish_date.strftime('%d.%m.%Y %H:%M')}\n\n"
                
                return summary
        except Exception as e:
            logger.error(f"Ошибка получения новостей по категории: {e}")
            return f"❌ Ошибка получения новостей #{category}"
    
    def get_news_stats(self) -> str:
        """Получение статистики новостей"""
        try:
            with get_db_session() as session:
                total_news = session.query(NewsItem).count()
                
                # Статистика по категориям
                categories = session.query(NewsItem.category, func.count(NewsItem.id)).group_by(NewsItem.category).all()
                
                stats = f"📊 <b>Статистика новостей:</b>\n\n"
                stats += f"📰 Всего новостей: <b>{total_news}</b>\n\n"
                
                if categories:
                    stats += "📈 По категориям:\n"
                    for category, count in categories:
                        if category:
                            stats += f"   #{category}: <b>{count}</b>\n"
                
                # Последние источники
                recent_sources = session.query(NewsSource).filter(NewsSource.is_active == True).limit(5).all()
                if recent_sources:
                    stats += f"\n📡 Активные источники: <b>{len(recent_sources)}</b>\n"
                    for source in recent_sources:
                        stats += f"   • {source.name}\n"
                
                return stats
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return "❌ Ошибка получения статистики"
    
    def send_news_with_media(self, chat_id: int, news_id: int) -> bool:
        """Отправка конкретной новости с медиа"""
        try:
            with get_db_session() as session:
                news = session.query(NewsItem).filter(NewsItem.id == news_id).first()
                
                if not news:
                    self.send_message(chat_id, "❌ Новость не найдена")
                    return False
                
                # Формируем текст новости
                text = f"📰 <b>{news.title}</b>\n\n"
                
                if news.content_html:
                    # Убираем HTML теги для Telegram
                    import re
                    clean_content = re.sub(r'<[^>]+>', '', news.content_html)
                    text += f"{clean_content[:500]}...\n\n" if len(clean_content) > 500 else f"{clean_content}\n\n"
                elif news.content:
                    text += f"{news.content[:500]}...\n\n" if len(news.content) > 500 else f"{news.content}\n\n"
                
                text += f"📍 Источник: {news.source.name if news.source else 'Unknown'}\n"
                text += f"📅 Дата: {news.publish_date.strftime('%d.%m.%Y %H:%M')}\n"
                text += f"🏷️ Категория: #{news.category or 'general'}\n"
                
                if news.link:
                    text += f"🔗 <a href='{news.link}'>Читать полностью</a>"
                
                # Если есть медиа, отправляем с фото
                if news.media and isinstance(news.media, list) and len(news.media) > 0:
                    media_item = news.media[0]
                    if media_item.get('type') == 'photo' and media_item.get('url'):
                        return self.send_photo(chat_id, media_item['url'], text)
                
                # Иначе отправляем просто текст
                return self.send_message(chat_id, text)
                
        except Exception as e:
            logger.error(f"Ошибка отправки новости: {e}")
            return False
    
    def handle_command(self, chat_id: int, command: str, args: List[str] = None) -> bool:
        """Обработка команд бота"""
        try:
            if command == "/start":
                welcome_text = """
🤖 <b>Добро пожаловать в Gift Propaganda News Bot!</b>

📰 Я помогу вам получать свежие новости из канала @nextgen_NFT и других источников.

<b>Доступные команды:</b>
/start - Показать это сообщение
/news - Последние новости
/nft - Новости NFT
/crypto - Крипто новости
/stats - Статистика
/help - Помощь

Нажмите на кнопки ниже для быстрого доступа к новостям!
"""
                keyboard = [
                    [{"text": "📰 Последние новости", "callback_data": "news"}],
                    [{"text": "🖼️ NFT", "callback_data": "nft"}, {"text": "₿ Крипто", "callback_data": "crypto"}],
                    [{"text": "📊 Статистика", "callback_data": "stats"}]
                ]
                return self.send_inline_keyboard(chat_id, welcome_text, keyboard)
            
            elif command == "/news":
                text = self.get_news_summary(5)
                return self.send_message(chat_id, text)
            
            elif command == "/nft":
                text = self.get_news_by_category("nft", 5)
                return self.send_message(chat_id, text)
            
            elif command == "/crypto":
                text = self.get_news_by_category("crypto", 5)
                return self.send_message(chat_id, text)
            
            elif command == "/stats":
                text = self.get_news_stats()
                return self.send_message(chat_id, text)
            
            elif command == "/help":
                help_text = """
❓ <b>Помощь по использованию бота</b>

<b>Команды:</b>
/news - Показать последние новости
/nft - Новости из категории NFT
/crypto - Криптовалютные новости
/stats - Статистика новостей

<b>Автоматические обновления:</b>
Бот проверяет новые посты каждые 5 минут и автоматически добавляет их в базу данных.

<b>Источники:</b>
• @nextgen_NFT - основной канал
• RSS источники: VC.ru, CoinDesk, Cointelegraph, Habr NFT

По всем вопросам обращайтесь к администратору.
"""
                return self.send_message(chat_id, help_text)
            
            else:
                return self.send_message(chat_id, "❓ Неизвестная команда. Используйте /help для справки.")
                
        except Exception as e:
            logger.error(f"Ошибка обработки команды: {e}")
            return self.send_message(chat_id, "❌ Произошла ошибка при обработке команды")

# Создаем глобальный экземпляр бота
bot = TelegramBot() 