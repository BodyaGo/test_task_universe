# Brand Monitor - Real-time Reddit Monitoring Agent

Потужний агент для моніторингу бренду в реальному часі на Reddit з використанням штучного інтелекту для виявлення загроз, аналізу тональності та генерації рекомендацій щодо реагування.

## 🚀 Особливості

- **Real-time моніторинг Reddit** - Автоматичне сканування згадок бренду
- **AI-аналіз тональності** - Визначення позитивних, негативних та нейтральних згадок
- **Виявлення загроз** - Автоматична класифікація рівня загрози (низький, середній, високий, критичний)
- **Рекомендації щодо реагування** - AI-генеровані поради щодо відповіді на загрози
- **Інтерактивний дашборд** - Сучасний веб-інтерфейс для моніторингу
- **Аналітика та звіти** - Детальна статистика та тренди
- **Система алертів** - Налаштовувані сповіщення про загрози

## 🏗️ Архітектура

```
├── backend/          # Python FastAPI сервер
│   ├── app/
│   │   ├── api/      # REST API endpoints
│   │   ├── core/     # Конфігурація та база даних
│   │   ├── models/   # Pydantic моделі
│   │   ├── services/ # Бізнес-логіка
│   │   └── utils/    # Допоміжні функції
│   └── requirements.txt
├── frontend/         # Next.js React додаток
│   ├── src/
│   │   ├── app/      # App Router сторінки
│   │   ├── components/ # React компоненти
│   │   └── lib/      # API клієнт та утиліти
│   └── package.json
└── config/           # Конфігураційні файли
```

## 🛠️ Технології

### Backend
- **FastAPI** - Сучасний веб-фреймворк для Python
- **PRAW** - Python Reddit API Wrapper
- **OpenAI GPT** - Аналіз контексту та генерація рекомендацій
- **Transformers** - Аналіз тональності
- **MongoDB** - NoSQL база даних
- **Redis** - Кешування та черги
- **Celery** - Асинхронні задачі

### Frontend
- **Next.js 14** - React фреймворк з App Router
- **TypeScript** - Типізована JavaScript
- **Tailwind CSS** - Utility-first CSS фреймворк
- **Recharts** - Графіки та візуалізація
- **Heroicons** - Іконки
- **Axios** - HTTP клієнт

## 📋 Передумови

- Python 3.9+
- Node.js 18+
- MongoDB 5.0+
- Redis 6.0+
- Reddit API ключі
- OpenAI API ключ

## ⚡ Швидкий старт

### 1. Клонування репозиторію

```bash
git clone <repository-url>
cd brand-monitor
```

### 2. Налаштування Backend

```bash
cd backend

# Створення віртуального середовища
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Встановлення залежностей
pip install -r requirements.txt

# Копіювання конфігурації
cp .env.example .env
```

### 3. Конфігурація змінних середовища

Відредагуйте файл `backend/.env`:

```env
# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=BrandMonitor/1.0
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=brand_monitor

# Redis
REDIS_URL=redis://localhost:6379

# Моніторинг
BRAND_KEYWORDS=your_brand,your_product,your_company
MONITOR_SUBREDDITS=all,technology,business,reviews
```

### 4. Запуск Backend

```bash
# Запуск MongoDB та Redis (якщо не запущені)
# mongod
# redis-server

# Запуск FastAPI сервера
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Налаштування Frontend

```bash
cd frontend

# Встановлення залежностей
npm install

# Створення файлу змінних середовища
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Запуск development сервера
npm run dev
```

### 6. Доступ до додатку

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📊 Використання

### Дашборд

Головна сторінка показує:
- Загальну статистику згадок
- Розподіл тональності
- Високопріоритетні загрози
- Останні згадки
- Графіки та аналітику

### API Endpoints

#### Згадки
- `GET /api/v1/mentions` - Отримати згадки з фільтрацією
- `GET /api/v1/mentions/{id}` - Отримати конкретну згадку
- `POST /api/v1/mentions/scan` - Запустити ручне сканування
- `PATCH /api/v1/mentions/{id}/review` - Позначити як переглянуте

#### Моніторинг
- `GET /api/v1/monitoring/status` - Статус моніторингу
- `GET /api/v1/monitoring/stats` - Статистика моніторингу
- `POST /api/v1/monitoring/start` - Запустити моніторинг
- `POST /api/v1/monitoring/stop` - Зупинити моніторинг

#### Аналітика
- `GET /api/v1/analytics/overview` - Загальний огляд
- `GET /api/v1/analytics/sentiment-trends` - Тренди тональності
- `GET /api/v1/analytics/threat-analysis` - Аналіз загроз

## 🔧 Конфігурація

### Ключові слова бренду

Налаштуйте ключові слова для моніторингу в `.env`:

```env
BRAND_KEYWORDS=your_brand,your_product,competitor_name
```

### Subreddits для моніторингу

```env
MONITOR_SUBREDDITS=all,technology,business,reviews,gaming
```

### Інтервал моніторингу

```env
MONITOR_INTERVAL=300  # секунди
```

### Поріг загрози

```env
THREAT_THRESHOLD=0.7  # 0.0 - 1.0
```

## 🚀 Продакшн

### Docker

```bash
# Збірка та запуск з Docker Compose
docker-compose up -d
```

### Ручне розгортання

1. Налаштуйте production базу даних MongoDB
2. Налаштуйте Redis для продакшну
3. Встановіть змінні середовища
4. Запустіть backend з Gunicorn:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

5. Зберіть та розгорніть frontend:

```bash
npm run build
npm start
```

## 🔍 Моніторинг та логування

### Логи

Логи зберігаються в:
- Backend: консоль та файли логів
- Frontend: браузерна консоль

### Метрики

- Кількість оброблених згадок
- Розподіл рівнів загроз
- Час відповіді API
- Статус компонентів системи

## 🛡️ Безпека

- Всі API ключі зберігаються в змінних середовища
- CORS налаштований для безпечного доступу
- Валідація даних на всіх рівнях
- Rate limiting для API endpoints

## 🤝 Внесок у розробку

1. Fork репозиторій
2. Створіть feature branch
3. Зробіть зміни
4. Додайте тести
5. Створіть Pull Request

## 📝 Ліцензія

MIT License - дивіться файл LICENSE для деталей.

## 🆘 Підтримка

Якщо у вас виникли проблеми:

1. Перевірте логи backend та frontend
2. Переконайтеся, що всі сервіси запущені
3. Перевірте конфігурацію API ключів
4. Створіть issue в репозиторії

## 🔄 Оновлення

```bash
# Оновлення backend залежностей
cd backend
pip install -r requirements.txt --upgrade

# Оновлення frontend залежностей
cd frontend
npm update
```# test_task_universe
