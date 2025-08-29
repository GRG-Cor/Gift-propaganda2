#!/usr/bin/env python3
"""
API endpoints для Telegram Bot
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from pydantic import BaseModel
from bot import bot
from sqlalchemy.orm import Session

from db import get_db_session, NewsItem, NewsSource
from services.auto_publisher import auto_publisher
from config import TOKEN, CHANNEL_ID, WEBHOOK_URL

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram"])

class TelegramUpdate(BaseModel):
    update_id: int
    message: Dict[str, Any] = None
    callback_query: Dict[str, Any] = None

@router.post("/webhook")
async def webhook_handler(request: Request):
    """Обработчик webhook от Telegram"""
    try:
        data = await request.json()
        logger.info(f"Получен webhook: {data}")
        
        # Обрабатываем сообщения
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            if text.startswith("/"):
                # Обрабатываем команды
                command = text.split()[0]
                args = text.split()[1:] if len(text.split()) > 1 else []
                bot.handle_command(chat_id, command, args)
            else:
                # Обычное сообщение
                bot.send_message(chat_id, "Привет! Используйте /help для списка команд.")
        
        # Обрабатываем callback queries
        elif "callback_query" in data:
            callback_query = data["callback_query"]
            chat_id = callback_query["message"]["chat"]["id"]
            data_text = callback_query["data"]
            
            await handle_callback_query(chat_id, data_text)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        return {"status": "error", "message": str(e)}

async def handle_message(message: Dict[str, Any]):
    """Обработка входящих сообщений"""
    try:
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        if not chat_id:
            logger.error("Не удалось получить chat_id")
            return
        
        logger.info(f"Получено сообщение от {chat_id}: {text}")
        
        # Обработка команд
        if text.startswith("/"):
            command_parts = text.split()
            command = command_parts[0]
            args = command_parts[1:] if len(command_parts) > 1 else []
            
            bot.handle_command(chat_id, command, args)
        else:
            # Обычное сообщение
            response_text = """
🤖 <b>Gift Propaganda News Bot</b>

Используйте команды для получения новостей:

📰 <b>Команды:</b>
/start - Главное меню
/news - Последние новости
/nft - Новости NFT
/crypto - Крипто новости
/stats - Статистика
/help - Помощь

Бот автоматически обновляет новости каждые 5 минут!
"""
            bot.send_message(chat_id, response_text)
            
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")

async def handle_callback_query(chat_id: int, data: str):
    """Обработка callback query (нажатия на кнопки)"""
    try:
        logger.info(f"Получен callback query от {chat_id}: {data}")
        
        # Обработка различных типов callback data
        if data == "news":
            text = bot.get_news_summary(5)
            bot.send_message(chat_id, text)
        elif data == "nft":
            text = bot.get_news_summary(5, category="nft")
            bot.send_message(chat_id, text)
        elif data == "crypto":
            text = bot.get_news_summary(5, category="crypto")
            bot.send_message(chat_id, text)
        elif data == "stats":
            text = bot.get_stats()
            bot.send_message(chat_id, text)
        else:
            bot.send_message(chat_id, "Неизвестная команда")
            
    except Exception as e:
        logger.error(f"Ошибка обработки callback query: {e}")

@router.get("/bot-info")
async def get_bot_info():
    """Получение информации о боте"""
    try:
        import requests
        from config import TOKEN
        
        url = f"https://api.telegram.org/bot{TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            return {
                "status": "ok",
                "bot_info": bot_info.get("result", {}),
                "webhook_url": f"{bot_info.get('result', {}).get('username', 'unknown')} bot"
            }
        else:
            return {
                "status": "error",
                "message": "Не удалось получить информацию о боте"
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения информации о боте: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/send-news")
async def send_news_to_chat(chat_id: int, news_id: int = None):
    """Отправка новостей в конкретный чат"""
    try:
        if news_id:
            # Отправка конкретной новости
            success = bot.send_news_with_media(chat_id, news_id)
        else:
            # Отправка сводки новостей
            text = bot.get_news_summary(3)
            success = bot.send_message(chat_id, text)
        
        return {
            "status": "ok" if success else "error",
            "chat_id": chat_id,
            "news_id": news_id
        }
        
    except Exception as e:
        logger.error(f"Ошибка отправки новостей: {e}")
        return {
            "status": "error",
            "message": str(e)
        } 

@router.post("/publish-now")
async def publish_news_now(background_tasks: BackgroundTasks):
    """
    Принудительно публикует неопубликованные новости в канал
    """
    try:
        # Запускаем публикацию в фоновом режиме (force=True для ручной публикации)
        background_tasks.add_task(auto_publisher.publish_batch, force=True)
        
        return {
            "message": "Publishing started in background",
            "status": "started"
        }
    except Exception as e:
        logger.error(f"Error starting manual publish: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/publish-status")
async def get_publish_status(db: Session = Depends(get_db_session)):
    """
    Получает статус автоматической публикации
    """
    try:
        # Подсчитываем статистику
        total_news = db.query(NewsItem).count()
        published_news = db.query(NewsItem).filter(NewsItem.is_published_to_channel == True).count()
        unpublished_news = db.query(NewsItem).filter(NewsItem.is_published_to_channel == False).count()
        
        return {
            "auto_publish_enabled": AUTO_PUBLISH_ENABLED,
            "channel_id": CHANNEL_ID,
            "statistics": {
                "total_news": total_news,
                "published_news": published_news,
                "unpublished_news": unpublished_news
            },
            "settings": {
                "interval_seconds": auto_publisher.interval,
                "batch_limit": auto_publisher.limit,
                "signature": auto_publisher.signature
            }
        }
    except Exception as e:
        logger.error(f"Error getting publish status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/published-news")
async def get_published_news(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db_session)
):
    """
    Получает список опубликованных новостей
    """
    try:
        published_news = db.query(NewsItem).filter(
            NewsItem.is_published_to_channel == True
        ).order_by(NewsItem.published_to_channel_at.desc()).offset(offset).limit(limit).all()
        
        result = []
        for news in published_news:
            source = db.query(NewsSource).filter(NewsSource.id == news.source_id).first()
            result.append({
                "id": news.id,
                "title": news.title,
                "category": news.category,
                "published_at": news.published_to_channel_at.isoformat() if news.published_to_channel_at else None,
                "telegram_message_id": news.telegram_message_id,
                "source_name": source.name if source else None,
                "link": news.link
            })
        
        return {
            "published_news": result,
            "total": len(result)
        }
    except Exception as e:
        logger.error(f"Error getting published news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish-specific/{news_id}")
async def publish_specific_news(news_id: int, db: Session = Depends(get_db_session)):
    """
    Публикует конкретную новость в канал
    """
    try:
        # Получаем новость
        news_item = db.query(NewsItem).filter(NewsItem.id == news_id).first()
        if not news_item:
            raise HTTPException(status_code=404, detail="News not found")
        
        # Проверяем, не опубликована ли уже
        if news_item.is_published_to_channel:
            return {
                "message": "News already published",
                "telegram_message_id": news_item.telegram_message_id,
                "published_at": news_item.published_to_channel_at.isoformat() if news_item.published_to_channel_at else None
            }
        
        # Публикуем
        message_id = await auto_publisher.publish_news_to_channel(news_item)
        
        if message_id:
            return {
                "message": "News published successfully",
                "telegram_message_id": message_id,
                "news_id": news_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to publish news")
    except Exception as e:
        logger.error(f"Error publishing specific news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-bot")
async def test_bot():
    """Тестовый эндпоинт для проверки работы бота"""
    try:
        # Проверяем информацию о боте
        url = f"https://api.telegram.org/bot{TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            return {
                "status": "success",
                "bot_info": bot_info,
                "webhook_url": f"{WEBHOOK_URL}/telegram/webhook",
                "channel_id": CHANNEL_ID
            }
        else:
            return {
                "status": "error",
                "message": f"Ошибка получения информации о боте: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.delete("/unpublish/{news_id}")
async def unpublish_news(news_id: int, db: Session = Depends(get_db_session)):
    """
    Отменяет публикацию новости (удаляет из канала)
    """
    try:
        # Получаем новость
        news_item = db.query(NewsItem).filter(NewsItem.id == news_id).first()
        if not news_item:
            raise HTTPException(status_code=404, detail="News not found")
        
        if not news_item.is_published_to_channel or not news_item.telegram_message_id:
            raise HTTPException(status_code=400, detail="News is not published")
        
        # Удаляем сообщение из канала
        import requests
        response = requests.post(
            f"https://api.telegram.org/bot{auto_publisher.token}/deleteMessage",
            data={
                'chat_id': auto_publisher.channel_id,
                'message_id': news_item.telegram_message_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                # Обновляем статус в базе данных
                news_item.is_published_to_channel = False
                news_item.published_to_channel_at = None
                news_item.telegram_message_id = None
                db.commit()
                
                return {
                    "message": "News unpublished successfully",
                    "news_id": news_id
                }
            else:
                raise HTTPException(status_code=500, detail=f"Telegram API error: {result}")
        else:
            raise HTTPException(status_code=500, detail=f"HTTP error {response.status_code}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unpublishing news {news_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channel-info")
async def get_channel_info():
    """
    Получает информацию о канале
    """
    try:
        import requests
        
        # Получаем информацию о канале
        response = requests.get(
            f"https://api.telegram.org/bot{auto_publisher.token}/getChat",
            data={'chat_id': auto_publisher.channel_id},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                chat_info = result['result']
                return {
                    "channel_id": auto_publisher.channel_id,
                    "title": chat_info.get('title'),
                    "description": chat_info.get('description'),
                    "member_count": chat_info.get('member_count'),
                    "type": chat_info.get('type')
                }
            else:
                return {
                    "channel_id": auto_publisher.channel_id,
                    "error": f"Telegram API error: {result}"
                }
        else:
            return {
                "channel_id": auto_publisher.channel_id,
                "error": f"HTTP error {response.status_code}"
            }
            
    except Exception as e:
        logger.error(f"Error getting channel info: {e}")
        return {
            "channel_id": auto_publisher.channel_id,
            "error": str(e)
        } 


