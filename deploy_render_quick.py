#!/usr/bin/env python3
"""
Скрипт для быстрого деплоя на Render
Запускает проект 24/7 на бесплатном хостинге
"""

import os
import subprocess
import sys

def check_git_status():
    """Проверяет статус git репозитория"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("⚠️  Есть несохраненные изменения!")
            print("Рекомендуется сделать commit перед деплоем")
            return False
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при проверке git статуса")
        return False

def push_to_github():
    """Пушит изменения в GitHub"""
    try:
        print("📤 Отправка изменений в GitHub...")
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Deploy to Render'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("✅ Изменения отправлены в GitHub")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при отправке в GitHub: {e}")
        return False

def main():
    print("🚀 Деплой на Render - 24/7 хостинг")
    print("=" * 50)
    
    # Проверяем git статус
    if not check_git_status():
        response = input("Продолжить деплой? (y/N): ")
        if response.lower() != 'y':
            print("❌ Деплой отменен")
            return
    
    # Отправляем в GitHub
    if not push_to_github():
        print("❌ Не удалось отправить в GitHub")
        return
    
    print("\n🎉 Код отправлен в GitHub!")
    print("\n📋 Следующие шаги для деплоя на Render:")
    print("1. Перейдите на https://render.com")
    print("2. Создайте аккаунт или войдите")
    print("3. Нажмите 'New +' → 'Web Service'")
    print("4. Подключите ваш GitHub репозиторий")
    print("5. Настройте переменные окружения:")
    print("   - TOKEN=ваш_токен_бота")
    print("   - WEBHOOK_URL=https://ваш-сервис.onrender.com/webhook")
    print("6. Нажмите 'Create Web Service'")
    print("\n🔗 После деплоя ваш API будет доступен по адресу:")
    print("   https://ваш-сервис.onrender.com")
    print("\n📱 Не забудьте обновить URL API в фронтенде!")

if __name__ == "__main__":
    main()
