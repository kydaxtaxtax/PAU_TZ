# Инструкция по запуску проекта

Простой веб-инструмент для исследования пользовательского опыта с интеграцией LLM.

## Требования
- Docker
- Docker Compose

## Запуск

1. Перейдите в папку с проектом:
   ```bash
   cd project
   ```

2. Создайте файл `.env` в корне папки `project` и добавьте в него ваши учетные данные:
   ```env
   LLM_API_URL=https://api.hyperfusion.io/v1/chat/completions
   LLM_API_KEY=ваш_api_ключ
   ```

3. Запустите приложение в фоновом режиме:
   ```bash
   docker compose up -d --build
   ```

3. Откройте браузер и перейдите по адресу:
   [http://localhost](http://localhost)

## Остановка
Для остановки всех сервисов выполните:
```bash
docker compose down
```
