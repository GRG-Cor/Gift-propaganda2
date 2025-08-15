#!/usr/bin/env python3
"""
Скрипт для ручного деплоя проекта на GitHub Pages
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

def main():
    print("🚀 Запуск деплоя на GitHub Pages...")
    
    # Проверяем, что мы в корневой директории проекта
    if not Path("giftpropaganda-frontend").exists():
        print("❌ Ошибка: Не найден каталог giftpropaganda-frontend")
        print("Убедитесь, что вы находитесь в корневой директории проекта")
        sys.exit(1)
    
    # Переходим в директорию фронтенда
    os.chdir("giftpropaganda-frontend")
    
    print("\n📦 Установка зависимостей...")
    if not run_command("npm ci"):
        sys.exit(1)
    
    print("\n🔨 Сборка проекта...")
    if not run_command("npm run build"):
        sys.exit(1)
    
    print("\n🚀 Деплой на GitHub Pages...")
    if not run_command("npm run deploy"):
        sys.exit(1)
    
    print("\n✅ Деплой завершен успешно!")
    print("🌐 Ваш сайт будет доступен по адресу:")
    print("https://miroslav-mobydev.github.io/gift-propaganda")
    print("\n⏳ Подождите несколько минут, пока изменения применятся...")

if __name__ == "__main__":
    main() 