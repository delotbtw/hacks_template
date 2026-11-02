# Глоссарий

| Термин | Что это |
|---|---|
| FastAPI | Python-фреймворк для HTTP API; сам строит OpenAPI-схему и `/docs`. |
| SQLAlchemy | ORM: таблицы описываются классами (`app/models`), запросы — на Python. Здесь async. |
| Alembic | Миграции схемы БД: `make makemigration m="..."`, `make migrate`. |
| Redis | Быстрое key-value хранилище в памяти (кэш, счётчики, очереди). Здесь только проверка связи. |
| pytest | Запуск тестов: `make test`. |
| OpenAPI | Описание API в JSON (`contracts/openapi.json`), из него генерируется клиент фронта. |
| Prism | Мок-сервер, отвечающий по OpenAPI без реального бэкенда. |
| Repository | Слой доступа к БД (`app/repositories`). Сервис вызывает репозиторий, роутер — сервис. |
| Protocol | Интерфейс в Python (`typing.Protocol`): `Predictor`, `LLMClient`. |
