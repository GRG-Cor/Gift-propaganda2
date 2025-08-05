# 🚀 Деплой на Render

## Шаг 1: Подготовка репозитория

1. Убедитесь, что ваш код находится в GitHub репозитории
2. Проверьте, что все файлы на месте:
   - `requirements.txt`
   - `server/main.py`
   - `render.yaml`

## Шаг 2: Создание аккаунта на Render

1. Перейдите на [render.com](https://render.com)
2. Зарегистрируйтесь или войдите в аккаунт
3. Подключите ваш GitHub аккаунт

## Шаг 3: Создание сервиса

1. Нажмите **"New +"** → **"Web Service"**
2. Подключите ваш GitHub репозиторий
3. Настройте сервис:

### Основные настройки:
- **Name**: `giftpropaganda-api`
- **Environment**: `Python`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`

### Переменные окружения:
- `DATABASE_URL` - будет создана автоматически
- `TOKEN` - ваш Telegram бот токен
- `WEBHOOK_URL` - URL для webhook (например: `https://your-app.onrender.com/webhook`)

## Шаг 4: Создание базы данных

1. Нажмите **"New +"** → **"PostgreSQL"**
2. Настройте:
   - **Name**: `giftpropaganda-db`
   - **Database**: `giftpropaganda`
   - **User**: `giftpropaganda`

## Шаг 5: Подключение базы данных

1. В настройках вашего web сервиса
2. Добавьте переменную окружения:
   - **Key**: `DATABASE_URL`
   - **Value**: скопируйте из настроек PostgreSQL

## Шаг 6: Настройка переменных окружения

В настройках web сервиса добавьте:

```
TOKEN=your_telegram_bot_token
WEBHOOK_URL=https://your-app-name.onrender.com/webhook
```

## Шаг 7: Деплой

1. Нажмите **"Create Web Service"**
2. Render автоматически:
   - Установит зависимости
   - Соберет приложение
   - Запустит сервис

## 🔧 Проверка деплоя

### Проверьте логи:
1. Перейдите в ваш сервис на Render
2. Вкладка **"Logs"**
3. Убедитесь, что нет ошибок

### Проверьте API:
```
https://your-app-name.onrender.com/health
```

## 📱 Настройка бота

После успешного деплоя обновите webhook:

```python
import requests

url = f"https://api.telegram.org/bot{YOUR_TOKEN}/setWebhook"
data = {
    "url": "https://your-app-name.onrender.com/webhook"
}
response = requests.post(url, json=data)
print(response.json())
```

## 🌐 Обновление фронтенда

Обновите URL API в вашем React приложении:

```typescript
// В src/api/news.ts
const API_CONFIG = {
  PROD: 'https://your-app-name.onrender.com/api/news',
  // ...
};
```

## 🔧 Устранение проблем

### Проблема: Ошибка подключения к БД
- Проверьте `DATABASE_URL`
- Убедитесь, что база данных создана

### Проблема: Ошибка импорта
- Проверьте структуру папок
- Убедитесь, что `server/` папка на месте

### Проблема: Таймаут
- Проверьте логи в Render
- Убедитесь, что порт указан правильно

## 📞 Поддержка

- [Render Documentation](https://render.com/docs)
- [FastAPI на Render](https://render.com/docs/deploy-fastapi) 