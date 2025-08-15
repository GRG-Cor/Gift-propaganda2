# GiftNews - Новостной агрегатор

Проект новостного агрегатора с React фронтендом и Python бэкендом.

## 🌐 Живое приложение

**Ваше приложение доступно по адресу:**
👉 [https://miroslav-mobydev.github.io/gift-propaganda1/](https://miroslav-mobydev.github.io/gift-propaganda1/)

## 🚀 Быстрый деплой на GitHub Pages

### Автоматический деплой (рекомендуется)
1. Сделайте push в ветку `main`:
   ```bash
   git add .
   git commit -m "Update project"
   git push origin main
   ```

2. GitHub Actions автоматически задеплоит проект на GitHub Pages

### Ручной деплой
```bash
python3 deploy_manual.py
```

## 📁 Структура проекта

```
GiftNews-main/
├── giftpropaganda-frontend/     # React приложение
├── server/                      # Python бэкенд
├── .github/workflows/          # GitHub Actions
├── scripts/                    # Вспомогательные скрипты
└── README.md                   # Документация
```

## 🔧 Настройка

### 1. Переменные окружения
В настройках репозитория (Settings → Secrets and variables → Actions) добавьте:
- `REACT_APP_API_URL` - URL вашего API сервера

### 2. GitHub Pages
1. Перейдите в Settings → Pages
2. Выберите Source: "Deploy from a branch"
3. Выберите Branch: "gh-pages"
4. Нажмите Save

## 🌐 Доступ к сайту

После успешного деплоя сайт будет доступен по адресу:
**https://miroslav-mobydev.github.io/gift-propaganda1**

## 🛠️ Локальная разработка

### Frontend
```bash
cd giftpropaganda-frontend
npm install
npm start
```

### Backend
```bash
cd server
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

## 📚 Документация

- [Настройка GitHub Pages](GITHUB_PAGES_SETUP.md)
- [Скрипты деплоя](scripts/)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License 