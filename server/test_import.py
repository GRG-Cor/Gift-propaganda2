#!/usr/bin/env python3
"""
Тестовый файл для проверки импорта роутеров
"""

print("🔍 Тестирование импорта роутеров...")

try:
    print("1. Импортируем news router...")
    from api.news import router as news_router
    print("✅ News router импортирован успешно")
    print(f"   Routes: {[route.path for route in news_router.routes]}")
except Exception as e:
    print(f"❌ Ошибка импорта news router: {e}")

try:
    print("\n2. Импортируем telegram router...")
    from api.telegram import router as telegram_router
    print("✅ Telegram router импортирован успешно")
    print(f"   Routes: {[route.path for route in telegram_router.routes]}")
except Exception as e:
    print(f"❌ Ошибка импорта telegram router: {e}")

print("\n🔍 Тестирование завершено")
