#!/usr/bin/env python3
"""
Скрипт для подготовки к деплою на Render
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении: {command}")
        print(f"Ошибка: {e.stderr}")
        return None

def check_files():
    """Проверяет наличие необходимых файлов"""
    required_files = [
        "requirements.txt",
        "server/main.py",
        "render.yaml"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Отсутствуют необходимые файлы:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Все необходимые файлы найдены")
    return True

def main():
    print("🚀 Подготовка к деплою на Render...")
    
    # Проверяем файлы
    if not check_files():
        sys.exit(1)
    
    print("\n📋 Инструкции по деплою:")
    print("1. Перейдите на https://render.com")
    print("2. Создайте новый Web Service")
    print("3. Подключите ваш GitHub репозиторий")
    print("4. Настройте переменные окружения:")
    print("   - TOKEN=your_telegram_bot_token")
    print("   - WEBHOOK_URL=https://your-app-name.onrender.com/webhook")
    print("5. Создайте PostgreSQL базу данных")
    print("6. Подключите DATABASE_URL к сервису")
    
    print("\n📁 Структура проекта для Render:")
    print("├── requirements.txt")
    print("├── render.yaml")
    print("├── server/")
    print("│   ├── main.py")
    print("│   ├── api/")
    print("│   ├── models.py")
    print("│   └── ...")
    print("└── ...")
    
    print("\n🔧 Настройки для Render:")
    print("- Environment: Python")
    print("- Build Command: pip install -r requirements.txt")
    print("- Start Command: uvicorn server.main:app --host 0.0.0.0 --port $PORT")
    
    print("\n✅ Готово к деплою!")
    print("📖 Подробные инструкции: RENDER_DEPLOY.md")

if __name__ == "__main__":
    main() 