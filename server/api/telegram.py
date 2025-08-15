#!/usr/bin/env python3
"""
API endpoints для Telegram Bot
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from server.bot import bot

logger = logging.getLogger(__name__)
router = APIRouter()

class TelegramUpdate(BaseModel):
    update_id: int
    message: Dict[str, Any] = None
    callback_query: Dict[str, Any] = None

@router.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Обработка webhook от Telegram"""
    try:
        logger.info(f"Получен webhook: {update.update_id}")
        
        # Обработка сообщений
        if update.message:
            await handle_message(update.message)
        
        # Обработка callback query (кнопки)
        elif update.callback_query:
            await handle_callback_query(update.callback_query)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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

async def handle_callback_query(callback_query: Dict[str, Any]):
    """Обработка callback query (нажатия на кнопки)"""
    try:
        chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
        data = callback_query.get("data")
        
        if not chat_id or not data:
            logger.error("Не удалось получить chat_id или data из callback_query")
            return
        
        logger.info(f"Получен callback query от {chat_id}: {data}")
        
        # Обработка различных типов callback data
        if data == "news":
            text = bot.get_news_summary(5)
            bot.send_message(chat_id, text)
            
        elif data == "nft":
            text = bot.get_news_by_category("nft", 5)
            bot.send_message(chat_id, text)
            
        elif data == "crypto":
            text = bot.get_news_by_category("crypto", 5)
            bot.send_message(chat_id, text)
            
        elif data == "stats":
            text = bot.get_news_stats()
            bot.send_message(chat_id, text)
            
        elif data.startswith("news_"):
            # Обработка выбора конкретной новости
            try:
                news_id = int(data.split("_")[1])
                bot.send_news_with_media(chat_id, news_id)
            except (ValueError, IndexError):
                bot.send_message(chat_id, "❌ Ошибка получения новости")
        
        else:
            bot.send_message(chat_id, "❓ Неизвестная команда")
            
    except Exception as e:
        logger.error(f"Ошибка обработки callback query: {e}")

@router.get("/bot-info")
async def get_bot_info():
    """Получение информации о боте"""
    try:
        import requests
        from server.config import TOKEN
        
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