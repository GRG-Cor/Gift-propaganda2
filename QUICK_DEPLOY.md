# 🚀 Быстрый деплой на GitHub Pages

## Шаг 1: Подготовка
```bash
# Добавить все изменения
git add .

# Создать коммит
git commit -m "Setup GitHub Pages deployment"

# Отправить в репозиторий
git push origin main
```

## Шаг 2: Настройка GitHub Pages
1. Перейдите в **Settings** вашего репозитория
2. В разделе **Pages** выберите:
   - Source: "Deploy from a branch"
   - Branch: "gh-pages"
   - Folder: "/ (root)"
3. Нажмите **Save**

## Шаг 3: Добавить переменные окружения
1. В **Settings** → **Secrets and variables** → **Actions**
2. Добавьте секрет:
   - Name: `REACT_APP_API_URL`
   - Value: URL вашего API сервера

## Шаг 4: Проверить деплой
1. Перейдите в **Actions** вкладку
2. Убедитесь, что workflow "Deploy to GitHub Pages" выполнился успешно
3. Сайт будет доступен по адресу: **https://miroslav-mobydev.github.io/gift-propaganda**

## Альтернативный способ (ручной деплой)
```bash
python3 deploy_manual.py
```

## 🔧 Устранение проблем

### Если деплой не работает:
1. Проверьте, что ветка называется `main` (не `master`)
2. Убедитесь, что в `package.json` правильно указан `homepage`
3. Проверьте переменные окружения в Secrets

### Если сайт не обновляется:
1. Очистите кэш браузера
2. Подождите 5-10 минут
3. Проверьте статус в Actions

## 📞 Поддержка
Если возникли проблемы, проверьте:
- [Подробная настройка](GITHUB_PAGES_SETUP.md)
- [README проекта](README.md) 