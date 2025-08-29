#!/usr/bin/env python3
"""
Telegram Bot для новостного агрегатора
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from config import TOKEN, WEBHOOK_URL
from db import get_db_session, NewsItem, NewsSource
from parsers.telegram_news_service import TelegramNewsService

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = TOKEN
        self.webhook_url = WEBHOOK_URL
        self.news_service = TelegramNewsService()
        
    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML"):
        """Отправка сообщения в чат"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"Сообщение отправлено в чат {chat_id}")
                return True
            else:
                logger.error(f"Ошибка отправки сообщения: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False
    
    def send_news_with_media(self, chat_id: int, news_id: int):
        """Отправка новости с медиа"""
        try:
            db = get_db_session()
            news_item = db.query(NewsItem).filter(NewsItem.id == news_id).first()
            
            if not news_item:
                self.send_message(chat_id, "❌ Новость не найдена")
                return
            
            # Формируем текст новости
            text = f"""
📰 <b>{news_item.title}</b>

{news_item.content[:500]}{'...' if len(news_item.content) > 500 else ''}

📅 Дата: {news_item.publish_date.strftime('%d.%m.%Y %H:%M')}
🏷️ Категория: {news_item.category}
👤 Автор: {news_item.author or 'Не указан'}

🔗 <a href="{news_item.link}">Читать полностью</a>
"""
            
            # Отправляем с медиа если есть
            if news_item.image_url:
                self.send_photo(chat_id, news_item.image_url, text)
            elif news_item.video_url:
                self.send_video(chat_id, news_item.video_url, text)
            else:
                self.send_message(chat_id, text)
                
        except Exception as e:
            logger.error(f"Ошибка отправки новости: {e}")
            self.send_message(chat_id, "❌ Ошибка отправки новости")
        finally:
            if 'db' in locals():
                db.close()
    
    def send_photo(self, chat_id: int, photo_url: str, caption: str = ""):
        """Отправка фото"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
            data = {
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"Фото отправлено в чат {chat_id}")
                return True
            else:
                logger.error(f"Ошибка отправки фото: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка отправки фото: {e}")
            return False
    
    def send_video(self, chat_id: int, video_url: str, caption: str = ""):
        """Отправка видео"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendVideo"
            data = {
                "chat_id": chat_id,
                "video": video_url,
                "caption": caption,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"Видео отправлено в чат {chat_id}")
                return True
            else:
                logger.error(f"Ошибка отправки видео: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка отправки видео: {e}")
            return False
    
    def handle_command(self, chat_id: int, command: str, args: List[str]):
        """Обработка команд"""
        try:
            if command == "/start":
                self.send_start_message(chat_id)
            elif command == "/news":
                self.send_news_summary(chat_id, 5)
            elif command == "/nft":
                self.send_news_by_category(chat_id, "nft", 5)
            elif command == "/crypto":
                self.send_news_by_category(chat_id, "crypto", 5)
            elif command == "/gifts":
                self.send_news_by_category(chat_id, "gifts", 5)
            elif command == "/tech":
                self.send_news_by_category(chat_id, "tech", 5)
            elif command == "/stats":
                self.send_stats(chat_id)
            elif command == "/help":
                self.send_help_message(chat_id)
            elif command == "/publish":
                self.publish_to_channel(chat_id)
            else:
                self.send_message(chat_id, "❓ Неизвестная команда. Используйте /help для списка команд.")
                
        except Exception as e:
            logger.error(f"Ошибка обработки команды {command}: {e}")
            self.send_message(chat_id, "❌ Произошла ошибка при обработке команды")
    
    def send_start_message(self, chat_id: int):
        """Отправка приветственного сообщения"""
        text = """
🎁 <b>Добро пожаловать в Gift Propaganda News Bot!</b>

Я помогу вам быть в курсе последних новостей в мире:
• 🎁 Подарки и акции
• 💰 Криптовалюты
• 🖼️ NFT и цифровое искусство
• 💻 Технологии

📰 <b>Команды:</b>
/news - Последние новости
/nft - Новости NFT
/crypto - Крипто новости
/gifts - Подарки и акции
/tech - Технологии
/stats - Статистика
/publish - Опубликовать в канал
/help - Помощь

Бот автоматически обновляет новости каждые 5 минут!
"""
        self.send_message(chat_id, text)
    
    def send_help_message(self, chat_id: int):
        """Отправка справки"""
        text = """
📚 <b>Справка по командам:</b>

/news - Показать последние 5 новостей
/nft - Новости NFT и цифрового искусства
/crypto - Новости криптовалют и блокчейна
/gifts - Подарки, акции и промокоды
/tech - Новости технологий и IT
/stats - Статистика новостей
/publish - Опубликовать новости в канал
/help - Показать эту справку

💡 <b>Советы:</b>
• Используйте команды для получения новостей по категориям
• Бот автоматически обновляет новости
• Все ссылки ведут на оригинальные источники
"""
        self.send_message(chat_id, text)
    
    def send_news_summary(self, chat_id: int, limit: int = 5, category: str = None):
        """Отправка сводки новостей"""
        try:
            db = get_db_session()
            
            query = db.query(NewsItem)
            if category and category != "all":
                query = query.filter(NewsItem.category == category)
            
            news_items = query.order_by(NewsItem.publish_date.desc()).limit(limit).all()
            
            if not news_items:
                self.send_message(chat_id, "📭 Новостей пока нет")
                return
            
            text = f"📰 <b>Последние новости"
            if category:
                text += f" ({category})"
            text += ":</b>\n\n"
            
            for i, news in enumerate(news_items, 1):
                text += f"{i}. <b>{news.title}</b>\n"
                text += f"📅 {news.publish_date.strftime('%d.%m %H:%M')}\n"
                text += f"🏷️ {news.category}\n"
                text += f"🔗 <a href='{news.link}'>Читать</a>\n\n"
            
            self.send_message(chat_id, text)
            
        except Exception as e:
            logger.error(f"Ошибка отправки сводки новостей: {e}")
            self.send_message(chat_id, "❌ Ошибка получения новостей")
        finally:
            if 'db' in locals():
                db.close()
    
    def send_news_by_category(self, chat_id: int, category: str, limit: int = 5):
        """Отправка новостей по категории"""
        self.send_news_summary(chat_id, limit, category)
    
    def send_stats(self, chat_id: int):
        """Отправка статистики"""
        try:
            db = get_db_session()
            
            total_news = db.query(NewsItem).count()
            
            # Статистика по категориям
            categories_stats = {}
            categories = db.query(NewsItem.category).distinct().all()
            
            for cat in categories:
                if cat[0]:
                    count = db.query(NewsItem).filter(NewsItem.category == cat[0]).count()
                    categories_stats[cat[0]] = count
            
            text = "📊 <b>Статистика новостей:</b>\n\n"
            text += f"📰 Всего новостей: {total_news}\n\n"
            
            for category, count in categories_stats.items():
                emoji = {
                    'gifts': '🎁',
                    'crypto': '💰',
                    'nft': '🖼️',
                    'tech': '💻',
                    'community': '👥'
                }.get(category, '📢')
                text += f"{emoji} {category}: {count}\n"
            
            self.send_message(chat_id, text)
            
        except Exception as e:
            logger.error(f"Ошибка отправки статистики: {e}")
            self.send_message(chat_id, "❌ Ошибка получения статистики")
        finally:
            if 'db' in locals():
                db.close()
    
    def get_news_summary(self, limit: int = 5, category: str = None) -> str:
        """Получение сводки новостей в виде текста"""
        try:
            db = get_db_session()
            
            query = db.query(NewsItem)
            if category and category != "all":
                query = query.filter(NewsItem.category == category)
            
            news_items = query.order_by(NewsItem.publish_date.desc()).limit(limit).all()
            
            if not news_items:
                return "📭 Новостей пока нет"
            
            text = f"📰 <b>Последние новости"
            if category:
                text += f" ({category})"
            text += ":</b>\n\n"
            
            for i, news in enumerate(news_items, 1):
                text += f"{i}. <b>{news.title}</b>\n"
                text += f"📅 {news.publish_date.strftime('%d.%m %H:%M')}\n"
                text += f"🏷️ {news.category}\n"
                text += f"🔗 <a href='{news.link}'>Читать</a>\n\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Ошибка получения сводки новостей: {e}")
            return "❌ Ошибка получения новостей"
        finally:
            if 'db' in locals():
                db.close()
    
    def get_stats(self) -> str:
        """Получение статистики в виде текста"""
        try:
            db = get_db_session()
            
            total_news = db.query(NewsItem).count()
            
            # Статистика по категориям
            categories_stats = {}
            categories = db.query(NewsItem.category).distinct().all()
            
            for cat in categories:
                if cat[0]:
                    count = db.query(NewsItem).filter(NewsItem.category == cat[0]).count()
                    categories_stats[cat[0]] = count
            
            text = "📊 <b>Статистика новостей:</b>\n\n"
            text += f"📰 Всего новостей: {total_news}\n\n"
            
            for category, count in categories_stats.items():
                emoji = {
                    'gifts': '🎁',
                    'crypto': '💰',
                    'nft': '🖼️',
                    'tech': '💻',
                    'community': '👥'
                }.get(category, '📢')
                text += f"{emoji} {category}: {count}\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return "❌ Ошибка получения статистики"
        finally:
            if 'db' in locals():
                db.close()
    
    def publish_to_channel(self, chat_id: int):
        """Публикация новостей в канал"""
        try:
            from services.auto_publisher import auto_publisher
            
            # Запускаем публикацию напрямую
            import asyncio
            
            # Создаем новую задачу для публикации
            async def publish_task():
                try:
                    await auto_publisher.publish_batch(force=True)
                    self.send_message(chat_id, "✅ Публикация новостей в канал завершена!")
                except Exception as e:
                    logger.error(f"Ошибка в задаче публикации: {e}")
                    self.send_message(chat_id, f"❌ Ошибка публикации: {str(e)}")
            
            # Запускаем задачу
            asyncio.create_task(publish_task())
            self.send_message(chat_id, "🚀 Публикация новостей в канал запущена...")
                
        except Exception as e:
            logger.error(f"Ошибка публикации в канал: {e}")
            self.send_message(chat_id, "❌ Ошибка при публикации в канал")

async def setup_webhook():
    """Установка webhook для Telegram бота"""
    try:
        webhook_url = f"{WEBHOOK_URL}/telegram/webhook"
        logger.info(f"Устанавливаем webhook: {webhook_url}")
        
        url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        data = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"]
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                logger.info("Webhook установлен успешно")
                return True
            else:
                logger.error(f"Ошибка установки webhook: {result}")
                return False
        else:
            logger.error(f"Ошибка HTTP при установке webhook: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка установки webhook: {e}")
        return False

# Создаем экземпляр бота
bot = TelegramBot() 