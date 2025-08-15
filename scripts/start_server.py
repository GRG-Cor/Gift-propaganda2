#!/usr/bin/env python3
"""
Скрипт для запуска сервера и тестирования API
"""

import subprocess
import time
import requests
import json
import sys
import os

def start_server():
    """Запускает сервер в фоновом режиме"""
    print("🚀 Запуск сервера...")
    
    # Запускаем сервер в фоновом режиме
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "server.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Ждем запуска сервера
    time.sleep(5)
    
    return process

def test_api():
    """Тестирует API endpoints"""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Тестирование API...")
    
    try:
        # Тест 1: Проверка здоровья сервера
        print("📡 Тест 1: Проверка здоровья сервера...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Сервер работает")
            print(f"   Ответ: {response.json()}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
        
        # Тест 2: Получение новостей
        print("\n📰 Тест 2: Получение новостей...")
        response = requests.get(f"{base_url}/api/news/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Получено {len(data['data'])} новостей")
            print(f"   Всего: {data['total']}")
            print(f"   Страница: {data['page']}")
            
            # Показываем первую новость
            if data['data']:
                first_news = data['data'][0]
                print(f"\n📝 Первая новость:")
                print(f"   Заголовок: {first_news['title']}")
                print(f"   Категория: {first_news['category']}")
                print(f"   Длина текста: {len(first_news['content'])} символов")
                print(f"   HTML контент: {len(first_news['content_html'])} символов")
                print(f"   Время чтения: {first_news['reading_time']} мин")
                print(f"   Просмотры: {first_news['views_count']}")
                
                if first_news.get('media'):
                    print(f"   Медиа: {len(first_news['media'])} элементов")
        else:
            print(f"❌ Ошибка получения новостей: {response.status_code}")
            return False
        
        # Тест 3: Фильтрация по категории
        print("\n🎯 Тест 3: Фильтрация по категории NFT...")
        response = requests.get(f"{base_url}/api/news/?category=nft")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Получено {len(data['data'])} NFT новостей")
        else:
            print(f"❌ Ошибка фильтрации: {response.status_code}")
        
        # Тест 4: Получение категорий
        print("\n📂 Тест 4: Получение категорий...")
        response = requests.get(f"{base_url}/api/categories/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Категории: {data['categories']}")
        else:
            print(f"❌ Ошибка получения категорий: {response.status_code}")
        
        # Тест 5: Статистика
        print("\n📊 Тест 5: Статистика...")
        response = requests.get(f"{base_url}/api/stats/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Статистика:")
            print(f"   Всего новостей: {data['total_news']}")
            print(f"   Категории: {data['categories']}")
        else:
            print(f"❌ Ошибка получения статистики: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def main():
    """Основная функция"""
    print("🎯 Запуск полного тестирования системы...")
    
    # Запускаем сервер
    server_process = start_server()
    
    try:
        # Тестируем API
        success = test_api()
        
        if success:
            print("\n🎉 Все тесты прошли успешно!")
            print("\n📱 Теперь можно открыть мини-апп:")
            print("   http://localhost:3000")
            print("\n🔗 API доступен по адресу:")
            print("   http://localhost:8000/docs")
            
            # Держим сервер запущенным
            print("\n⏸️  Сервер продолжает работать. Нажмите Ctrl+C для остановки...")
            try:
                server_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Остановка сервера...")
                
        else:
            print("\n❌ Тесты не прошли")
            
    except KeyboardInterrupt:
        print("\n🛑 Прерывание пользователем")
    finally:
        # Останавливаем сервер
        if server_process.poll() is None:
            server_process.terminate()
            server_process.wait()
            print("✅ Сервер остановлен")

if __name__ == "__main__":
    main() 