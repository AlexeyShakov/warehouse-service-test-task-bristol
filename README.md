# warehouse-service-test-task-bristol
# Сервис мониторинга состояния складов

<details>
<summary><strong>ТЗ (Task Description)</strong></summary>

## Требования

- Обязательное использование языка Python и фреймворка FastAPI для разработки микросервиса. Обязательное использование Kafka как брокера сообщений.
- Кандидат имеет свободу выбора технологий и библиотек(кроме указанных выше) для реализации остальных аспектов задачи.

## Сдача
Склонируйте проект, выполните задачу и пришлите ссылку на репозиторий.

## Задание
Вам предстоит разработать микросервис на языке Python, предназначенный для обработки сообщений от складов, которые уведомляют о приемках и отправках товаров.
Микросервис будет сохранять данные о перемещениях и предоставлять API для получения информации о конкретных перемещениях и текущих состояниях складов.

### Основные задачи

1. Обрабатывать сообщения, поступающие из очереди Kafka. Сообщения содержат информацию о приемке или отправке товаров на складах.
2. Сохранять информацию о каждом перемещении товара, включая отправителя, получателя, время, количество товаров, тип перемещения.
3. Учитывать, что количество товаров на складе не может быть меньше 0.
4. Предоставить информацию о текущем количестве товаров на складе.
5. Предоставить информацию о  перемещении товара, включая отправителя, получателя, время, прошедшее между отправкой и приемкой, а также разницу в количестве товара, если таковая имеется.
6. Предоставить OpenAPI спецификацию к API

### Примеры сообщений в Kafka
###### Прибытие
```json
{
    "id": "b3b53031-e83a-4654-87f5-b6b6fb09fd99", // id сообщения
    "source": "WH-3423", // источник отправки. формат - WH-****
    "specversion": "1.0",
    "type": "ru.retail.warehouses.movement",
    "datacontenttype": "application/json",
    "dataschema": "ru.retail.warehouses.movement.v1.0",
    "time": 1737439421623,
    "subject": "WH-3423:ARRIVAL",
    "destination": "ru.retail.warehouses",
    "data": {
        "movement_id": "c6290746-790e-43fa-8270-014dc90e02e0", // id перемещения. Одинаковое для отправки/приемки
        "warehouse_id": "c1d70455-7e14-11e9-812a-70106f431230", // id склада
        "timestamp": "2025-02-18T14:34:56Z", // время приемки
        "event": "arrival", // тип события
        "product_id": "4705204f-498f-4f96-b4ba-df17fb56bf55", // id товара
        "quantity": 100 // количество товара
    }
}
```
Отбытие

```json
{
    "id": "b3b53031-e83a-4654-87f5-b6b6fb09fd99",
    "source": "WH-3322",
    "specversion": "1.0",
    "type": "ru.retail.warehouses.movement",
    "datacontenttype": "application/json",
    "dataschema": "ru.retail.warehouses.movement.v1.0",
    "time": 1737439421623,
    "subject": "WH-3322:DEPARTURE",
    "destination": "ru.retail.warehouses",
    "data": {
        "movement_id": "c6290746-790e-43fa-8270-014dc90e02e0", // id перемещения. Одинаковое для отправки/приемки
        "warehouse_id": "25718666-6af6-4281-b5a6-3016e36fa557", // id склада
        "timestamp": "2025-02-18T12:12:56Z", // время отбытия
        "event": "departure", // тип события
        "product_id": "4705204f-498f-4f96-b4ba-df17fb56bf55", // id товара
        "quantity": 100 // количество товара
    }
}
```
Дополнительные задачи (опционально):
Реализовать систему кэширования для повышения скорости ответов на запросы API.

Настроить мониторинг сервиса для отслеживания его состояния и производительности.

Покрыть кода тестами.

Провести нагрузочное тестирование и предоставить график, иллюстрирующий, как приложение ведет себя под разной нагрузкой.

Спецификация API
Основные эндпоинты:
1. Получение информации о перемещении
URL: /api/movements/<movement_id>

Метод: GET

Описание: Возвращает информацию о перемещении по его ID...

2. Получение информации о состоянии склада
URL: /api/warehouses/<warehouse_id>/products/<product_id>

Метод: GET

Описание: Возвращает информацию текущем запасе товара...
</details>

<details>
<summary><strong>Реализация (Implementation)</strong></summary>

## Архитектура проекта

Проект построен с использованием **FastAPI** и асинхронного консьюмера Kafka. Основная логика разбита на следующие слои:

- `domains/` — бизнес-логика и модели предметной области
- `infrastructure/` — взаимодействие с Kafka и MongoDB
- `routers/` — описание REST-эндпоинтов
- `serializers/` — сериализация и десериализация сообщений из Kafka и ответов API
- `main.py` — инициализация FastAPI-приложения и фоновая задача консьюмера Kafka

## Стек технологий

| Компонент        | Используемое решение           |
|------------------|--------------------------------|
| Язык             | Python 3.11                    |
| Web Framework    | FastAPI                        |
| Kafka Client     | aiokafka (асинхронный)         |
| БД               | MongoDB (через `motor`)        |
| Валидация данных | Pydantic                       |
| Тестирование     | pytest (опционально)           |
| Dev-инструменты  | Poetry, Ruff, MyPy, pre-commit |
| Контейнеризация  | Docker + docker-compose        |
| Кэширование      | redis  + fastapi-cache2        |
| сli команды      | typer                          |


## API

REST API реализован в `routers/movements.py` и `routers/warehouses.py`:

- `GET /api/movements/{movement_id}` — получить детали перемещения
- `GET /api/warehouses/{warehouse_id}/products/{product_id}` — текущее количество товара на складе

Swagger-документация доступна по адресу `http://127.0.0.1/docs`.

## Docker

Сервис полностью контейнеризирован и запускается через `docker-compose`. Контейнеры:

- `warehouse_api` — FastAPI-приложение
- `kafka` — Kafka брокер (Confluent KRaft mode)
- `warehouse_state_db` — MongoDB
- `nginx` — обратный прокси (опционально)

Каждый сервис имеет `healthcheck` для контроля готовности.

## Dev-инфраструктура

- Используется `pre-commit` для автоформатирования и lint’а кода
- Poetry управляет зависимостями и виртуальным окружением
- В `.env` вынесены все чувствительные параметры (пароли, URI и т.д.)

## Заполнение БД

### Описание
Для автоматическго заполнения БД можно воспользоваться cli-командой. В директории src/utils/data лежит файл
test_warehouse_events.json. Это тестовый набор данных. Для того, чтобы загрузить свой набор данных, нужно положить в эту
директорию файл warehouse_events.json с нужными данными. Пайплайн команды:

1. Читается файл.
2. Kafka producer кладет данные в броке
3. Консьюмер получает данные
4. Данные проходят через все проверки и попадают в БД, если они валидные
5. Можно проверить, что все работает, воспользовавшись API http://127.0.0.1/docs

### Запуск команды

```docker exec -it warehouse_api poetry run warehouse-cli```

## Кэширование(опционально)
В проект добавлена поддержка кэширования через Redis с использованием библиотеки fastapi-cache2.
Это позволяет ускорить ответы от API на часто запрашиваемые ресурсы (например, информацию о состоянии склада).

Как это работает:
* Redis-клиент инициализируется при старте приложения в lifespan.

* кэш применяется к эндпоинтам с помощью декоратора @cache:

## Запуск приложения

1. Для начала нужно склонировать приложение с помощью команды:
```
git clone https://github.com/AlexeyShakov/warehouse-service-test-task-bristol.git
```
2. В корень проекта нужно добавить файл .env и заполнить его нужными данными. На данный момент нужны следующие переменные

| Переменная                 | Назначение                                                 |
|----------------------------|------------------------------------------------------------|
| `DB_PORT`                  | Порт MongoDB по умолчанию — `27017`                        |
| `MONGO_INITDB_ROOT_USERNAME` | Имя пользователя для MongoDB                               |
| `MONGO_INITDB_ROOT_PASSWORD` | Пароль пользователя MongoDB                                |
| `MONGO_HOST`               | Хост MongoDB (в docker-compose — это `warehouse_state_db`) |
| `MONGO_DB_NAME`            | Название базы данных MongoDB, по умолчанию — `warehouse`   |
| `KAFKA_CLUSTER_ID`         | Идентификатор Kafka-кластера                               |
| `CLUSTER_ID`               | Дублирует `KAFKA_CLUSTER_ID`                               |
| `KAFKA_HOST`               | Хост Kafka-брокера (в docker-compose — это `kafka`)        |
| `KAFKA_TOPIC`              | Название Kafka-топика, из которого читаются события        |
| `REDIS HOST`               | Хост Redis-сервера (обычно redis в docker-compose)         |
| `REDIS PORT`               | Порт Redis (по умолчанию 6379)                             |
| `TTL`                      | Время жизни кэшированных данных в секундах (например, 300) |
| `MAX_CONCURRENT_SENDS`     | Количество задач, запускаемых конкуретно для заполнения БД |

3. Запуск приложение

```docker-compose up --build``` - при первом запуске

```docker-compose up``` - при повторных запусках
</details>
