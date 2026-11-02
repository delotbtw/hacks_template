# Шаблон для хакатонов

FastAPI + Postgres + Redis + React, заготовки под ML и LLM-агента. Сквозной пример — сущность `Item`.

## Как создать проект

На GitHub: **Use this template** → новый репозиторий → `git clone`.

## Быстрый старт

```bash
make install   # uv sync, pnpm install, pre-commit
make up        # db, redis, migrate, api, web (dev, с перезагрузкой)
```

Web: http://localhost:5173 · API docs: http://localhost:8000/docs · Админка: http://localhost:8000/admin
(перед хакатоном смените `ADMIN_PASSWORD` и `ADMIN_SECRET_KEY` в `.env`; `.env` создаётся из `.env.example`).

## Чек-лист перед первым использованием

Не проверено автором шаблона (нужен GitHub и ваш ноутбук):

- [ ] Репозиторий запушен на GitHub, включено Settings → General → **Template repository**.
- [ ] Settings → Actions → General → Workflow permissions: **Read and write**; после первого пуша в `main` проверить, что `images.yml` отработал и образы появились в Packages.
- [ ] Оффлайн-проверка (раздел ниже) пройдена на вашем ноутбуке.
- [ ] Прогрев с пустого кэша (`docker builder prune -af && make warm`) пройден на вашем диске Docker (≥ 10 ГБ); дальше кэш не чистить.
- [ ] В `.env` сменены `ADMIN_PASSWORD` и `ADMIN_SECRET_KEY`; у каждого участника свой `OPENAI_API_KEY`.

## Команды

`make help` выводит полный список. Основные:

| Команда | Что делает |
|---|---|
| `up` / `demo` | dev с reload / production-подобная сборка без reload и dev-зависимостей |
| `stop` / `down` / `restart` | остановить / удалить контейнеры (тома остаются) / перезапустить |
| `rm` | удалить всё вместе с данными БД (спросит подтверждение) |
| `test` | pytest в контейнере; `make test LOCAL=1` — локально через uv (нужны db и redis на localhost: `docker compose up -d db redis`) |
| `lint` / `fmt` / `typecheck` | Ruff / форматирование / ty (не блокирует) |
| `migrate` / `makemigration m="..."` | миграции |
| `contracts` / `front-gen` / `mock` | OpenAPI → `contracts/openapi.json` / клиент фронта / Prism |
| `warm` | прогрев кэшей (см. ниже) |
| `pull` / `save-images` / `load-images` | образы из GHCR / в файл / из файла |

## Структура

`app/` бэкенд (api → services → repositories → models) · `alembic/` миграции · `ml/` Predictor (stub/real) ·
`agent/` LLM-клиент и цикл агента · `web/` фронтенд · `contracts/` OpenAPI · `docker/`, `compose*.yaml` ·
`docs/` status, handoff, assumptions, demo, specs, adr · `TASKS.md` таблица срезов.

Отступления от ТЗ: фронт проксирует `/api` → бэкенд (dev: Vite, demo: nginx), поэтому CORS нужен только для прямых запросов; `compose.demo.yaml` — override для demo; цель `warm` в `Dockerfile.api` вместо полной сборки образа со всеми группами.

## Клиент фронта

`openapi-typescript` + `openapi-fetch`: типы генерируются из контракта, рантайм крошечный, без генерации кода клиента. Сгенерированный `web/src/api/schema.d.ts` **коммитится** (фронт собирается без бэкенда); обновляется `make front-gen`. TypeScript в `web/` закреплён на 5.x, так как `openapi-typescript` не работает с TypeScript 7.

## Группы зависимостей uv

Основная (бэкенд), `dev` (по умолчанию), `ml` (pandas, scikit-learn, jupyter), `llm` (openai). В образ api попадают основная + `dev`, в demo — только основная. Локально: `uv sync --group ml`.

## Прогрев и скорость сборки

`make warm` (с интернетом): тянет базовые образы, кладёт колёса **всех** групп (`ml`, `llm`) в кэш BuildKit (`Dockerfile.api`, цель `warm`), собирает образы, делает `uv sync --all-groups` и `pnpm install` на хосте. После этого сборка без `ml`/`llm` ничего не скачивает (проверено: 0 загрузок у uv, `downloaded 0` у pnpm). **Не чистите билдер-кэш перед хакатоном** (`docker builder prune`, «Clean up» в Docker Desktop). Docker-диску нужно ≥ 10 ГБ свободного места: на 7,8 ГБ VM кэш вместе с другими образами не помещался.

Слои: зависимости копируют только lock-файлы, поэтому правка кода слой зависимостей не пересобирает.

### Замеры (macOS, Docker Desktop, базовые образы уже скачаны, интернет есть)

| Сценарий | Время |
|---|---|
| Холодная сборка `make up` (кэш BuildKit очищен, группы dev) | ~30 с |
| Пересборка после правки файла в `app/` | ~3 с |
| Пересборка после добавления одной зависимости (из кэша uv) | ~7 с |
| `make warm` (кэш очищен) | ~50–70 с |

Холодная сборка с нуля, когда и базовые образы не скачаны, не измерялась.

## Образы в GHCR

`.github/workflows/images.yml` на каждый push в `main` публикует `ghcr.io/<owner>/<repo>/api` и `/web` (цель demo). Включить: Settings → Actions → General → Workflow permissions: *Read and write*. Если репозиторий приватный, вход: `echo $GITHUB_PAT | docker login ghcr.io -u <user> --password-stdin` (PAT со scope `read:packages`). Затем `make pull IMAGE_REGISTRY=ghcr.io/<owner>/<repo>`.

## Оффлайн-проверка (на вашем ноутбуке)

1. Дома, с интернетом: свежий клон, `make install`, `make warm`, `make demo`, `make save-images`.
2. Отключите интернет, не чистя кэш Docker.
3. `make demo` и `make test LOCAL=1` (или `make test`) должны отработать без сети. Если образы пропали: `make load-images`.

Тест миграций и дрейфа контракта создают служебные БД `app_test` и `app_migrations_test` на том же Postgres.
