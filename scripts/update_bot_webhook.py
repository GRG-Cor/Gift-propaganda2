#!/usr/bin/env python3
"""
Скрипт для обновления webhook бота
"""

import requests
import json

def update_bot_webhook():
    """Обновляем webhook бота"""
    print("🔄 Обновление webhook бота...")
    
    # Токен бота
    token = "8429342375:AAFl55U3d2jiq3bm4UNTyDrbB0rztFTio2I"
    
    # URL для webhook (локальный для тестирования)
    webhook_url = "https://giftpropaganda.onrender.com/webhook"
    
    try:
        # Получаем текущий webhook
        print("📡 Получение текущего webhook...")
        response = requests.get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
        webhook_info = response.json()
        
        if response.status_code == 200:
            print(f"✅ Текущий webhook: {webhook_info['result']['url']}")
        else:
            print(f"❌ Ошибка получения webhook: {webhook_info}")
            return
        
        # Устанавливаем новый webhook
        print(f"🔧 Установка webhook: {webhook_url}")
        set_response = requests.post(
            f"https://api.telegram.org/bot{token}/setWebhook",
            json={"url": webhook_url}
        )
        
        if set_response.status_code == 200:
            result = set_response.json()
            if result.get('ok'):
                print("✅ Webhook успешно обновлен!")
            else:
                print(f"❌ Ошибка установки webhook: {result}")
        else:
            print(f"❌ Ошибка запроса: {set_response.status_code}")
        
        # Проверяем результат
        print("🔍 Проверка результата...")
        check_response = requests.get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
        if check_response.status_code == 200:
            final_info = check_response.json()
            print(f"✅ Финальный webhook: {final_info['result']['url']}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    update_bot_webhook() 