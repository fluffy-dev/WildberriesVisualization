# Сервис аналитики товаров Wildberries

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/) [![Django 5.2](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/download/)

Простой сервис для парсинга и анализа данных о товарах с сайта Wildberries. Проект включает в себя бэкенд на Django с API, фоновый парсер на Celery и динамический фронтенд для фильтрации и визуализации данных.

![Демонстрация работы](./assets/demo.gif)

## ✨ Ключевые возможности

*   **Асинхронный парсер**: Сбор данных о товарах с Wildberries по URL категории, работающий в фоновом режиме.
*   **REST API**: Эндпоинт для получения списка товаров с поддержкой фильтрации по цене, рейтингу и количеству отзывов, а также с возможностью сортировки.
*   **Интерактивный фронтенд**:
    *   Динамическая таблица с товарами, которая обновляется без перезагрузки страницы.
    *   Фильтры для гибкой настройки выборки данных.
    *   Интерактивные графики для визуализации аналитики.
*   **Полная контейнеризация**: Проект полностью обернут в Docker, что обеспечивает быстрый запуск и консистентность окружения.

## 🛠️ Стек технологий

#### Backend
*   **Python 3.11**
*   **Django 5.2**
*   **Django REST Framework** для создания REST API.
*   **Celery** для выполнения фоновых задач (парсинга).
*   **PostgreSQL** в качестве основной базы данных.
*   **Redis** как брокер сообщений для Celery.

#### Frontend
*   **Vanilla JavaScript (ES6+)**: Без фреймворков для легковесности и простоты.
*   **Chart.js**: Для создания интерактивных графиков.
*   **noUiSlider**: Для удобного слайдера выбора диапазона цен.
*   **HTML5 / CSS3**

#### Инфраструктура
*   **Docker / Docker Compose**: для оркестрации и управления контейнерами.

## 🏛️ Архитектурные решения

При разработке проекта были приняты следующие ключевые решения:

1.  **Сервисный слой (Services & Selectors)**
    Проект следует принципам [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide). Бизнес-логика вынесена из Views и моделей в отдельные модули:
    *   `services.py`: Содержат логику, изменяющую состояние системы (создание/обновление данных, запуск парсинга).
    *   `selectors.py`: Содержат логику для получения данных из базы данных (фильтрация, выборка).
    Это делает код более чистым, тестируемым и переиспользуемым.

2.  **Асинхронный парсинг**
    Парсинг — это долгий процесс. Чтобы не заставлять пользователя ждать и не блокировать API, сбор данных выполняется асинхронно с помощью Celery. API-эндпоинт лишь инициирует задачу, которая выполняется в отдельном воркер-процессе.

3.  **Изолированное окружение**
    Весь проект (Django, PostgreSQL, Redis, Celery) запускается в Docker-контейнерах. Это решает проблему зависимостей, гарантирует, что окружение для разработки и продакшена идентично, и позволяет запустить проект одной командой.

## 🚀 Начало работы

Для запуска проекта на вашем компьютере должны быть установлены **Docker** и **Docker Compose**.

#### 1. Клонирование репозитория

```bash
git clone https://github.com/fluffy-dev/WildberriesVisualization.git
cd WildberriesVisualization
```

#### 2. Настройка окружения

Проект использует переменные окружения для конфигурации. Скопируйте файл-пример `.env.example` в `.env`:

```bash
# Для Linux / macOS
cp .env.example .env

# Для Windows
copy .env.example .env
```

Файл `.env` уже содержит все необходимые для локального запуска значения. Вам не нужно ничего менять.

#### 3. Сборка и запуск контейнеров

Выполните следующую команду в корневой директории проекта:

```bash
docker-compose up --build -d
```
Эта команда соберет Docker-образы для Django-приложения, запустит все необходимые сервисы в фоновом режиме (`-d`) и свяжет их вместе.

#### 4. Применение миграций базы данных

После первого запуска нужно создать таблицы в базе данных. Выполните команду:

```bash
docker-compose exec web python src/manage.py migrate
```

Проект запущен! Основной интерфейс доступен по адресу [http://localhost:8000](http://localhost:8000).

## ⚙️ Как пользоваться

#### Запуск парсера

Чтобы наполнить базу данных, нужно запустить задачу парсинга. Для этого отправьте POST-запрос на специальный API-эндпоинт.

**Пример с помощью cURL (для Windows CMD):**
```bash
curl -X POST http://localhost:8000/api/products/start-parsing/ -H "Content-Type: application/json" -d "{\"url\": \"https://www.wildberries.ru/catalog/elektronika/noutbuki-i-kompyutery/noutbuki-ultrabuki\"}"
```
> **Примечание**: Командная строка Windows требует экранирования двойных кавычек. Для более удобной работы рекомендуется использовать API-клиенты вроде [Postman](https://www.postman.com/) или [Insomnia](https://insomnia.rest/).

В ответ вы получите `{"message": "Parsing task has been started."}`. Процесс парсинга можно отслеживать в логах Celery-воркера:
```bash
docker-compose logs -f worker
```

#### Просмотр аналитики

После завершения парсинга откройте в браузере [http://localhost:8000](http://localhost:8000) и пользуйтесь интерактивными фильтрами и графиками.

## 🔧 Команды для разработки

Все команды выполняются через `docker-compose exec web`.

*   **Создать миграции** (после изменения моделей в `models.py`):
    ```bash
    docker-compose exec web python src/manage.py makemigrations
    ```

*   **Применить миграции**:
    ```bash
    docker-compose exec web python src/manage.py migrate
    ```

*   **Создать суперпользователя** (для доступа к админ-панели Django):
    ```bash
    docker-compose exec web python src/manage.py createsuperuser
    ```

*   **Остановить все контейнеры**:
    ```bash
    docker-compose down
    ```