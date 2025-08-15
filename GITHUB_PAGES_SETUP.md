# Настройка GitHub Pages для проекта GiftNews

## Шаги для настройки деплоя:

### 1. Настройка репозитория
1. Перейдите в настройки репозитория на GitHub
2. В разделе "Pages" выберите:
   - Source: "Deploy from a branch"
   - Branch: "gh-pages" (создастся автоматически)
   - Folder: "/ (root)"

### 2. Настройка переменных окружения
В настройках репозитория (Settings → Secrets and variables → Actions) добавьте:
- `REACT_APP_API_URL` - URL вашего API сервера

### 3. Активация GitHub Pages
1. После первого деплоя перейдите в Settings → Pages
2. Убедитесь, что выбрана ветка `gh-pages`
3. Сайт будет доступен по адресу: `https://[username].github.io/[repository-name]`

### 4. Проверка деплоя
1. Запустите workflow вручную через Actions → Deploy to GitHub Pages → Run workflow
2. Или сделайте push в ветку main
3. Проверьте статус в разделе Actions

### 5. Возможные проблемы и решения

#### Проблема: 404 ошибка
- Убедитесь, что в `package.json` правильно указан `homepage`
- Проверьте, что ветка `gh-pages` создалась

#### Проблема: Сайт не обновляется
- Очистите кэш браузера
- Проверьте, что workflow завершился успешно

#### Проблема: API не работает
- Проверьте переменную `REACT_APP_API_URL` в secrets
- Убедитесь, что API сервер доступен

### 6. Локальная разработка
Для локальной разработки используйте:
```bash
cd giftpropaganda-frontend
npm start
```

### 7. Ручной деплой (если нужно)
```bash
cd giftpropaganda-frontend
npm run deploy
```

## Структура проекта
- `giftpropaganda-frontend/` - React приложение
- `.github/workflows/deploy.yml` - GitHub Actions workflow
- `GITHUB_PAGES_SETUP.md` - этот файл с инструкциями 