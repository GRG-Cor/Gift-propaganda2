# 🚀 Настройка GitHub Pages

## Шаг 1: Включите GitHub Pages
1. Перейдите в ваш репозиторий: https://github.com/Miroslav-mobyDev/gift-propaganda
2. Нажмите **Settings** (вкладка)
3. Прокрутите вниз до **Pages**
4. В разделе **Source** выберите **Deploy from a branch**
5. Выберите ветку **gh-pages** (создастся автоматически)
6. Нажмите **Save**

## Шаг 2: Настройте переменные окружения
1. В репозитории перейдите в **Settings** → **Secrets and variables** → **Actions**
2. Нажмите **New repository secret**
3. Добавьте:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://your-api-url.onrender.com` (замените на ваш API URL)

## Шаг 3: Запустите деплой
1. Сделайте push в main ветку:
   ```bash
   git add .
   git commit -m "Setup GitHub Pages deployment"
   git push origin main
   ```

## Шаг 4: Проверьте деплой
1. Перейдите в **Actions** вкладку
2. Убедитесь, что workflow выполнился успешно
3. Ваше приложение будет доступно по адресу:
   **https://miroslav-mobydev.github.io/gift-propaganda**

## 🎉 Результат
После успешного деплоя вы получите:
- **Frontend**: https://miroslav-mobydev.github.io/gift-propaganda
- **API**: https://your-api-url.onrender.com (нужно задеплоить отдельно)

## 📱 Для бота
Обновите код бота, чтобы он отправлял ссылку:
```
https://miroslav-mobydev.github.io/gift-propaganda
``` 