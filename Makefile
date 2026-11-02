.DEFAULT_GOAL := help
SHELL := /bin/bash

COMPOSE      := docker compose
COMPOSE_DEMO := docker compose -f compose.yaml -f compose.demo.yaml
IMAGES       := hackathon-api:demo hackathon-web:demo
IMAGES_TAR   := images/hackathon-images.tar

-include .env
API_PORT ?= 8000
WEB_PORT ?= 5173
MOCK_PORT ?= 4010

.PHONY: help install warm up demo stop down restart rm logs ps shell db-shell migrate makemigration test lint fmt typecheck contracts front-gen mock pull save-images load-images
help: ## Список команд
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.env:
	cp .env.example .env
	@echo "Создан .env из .env.example — смените ADMIN_PASSWORD и ключи"

define urls
	@echo ""; echo "  Web:   http://localhost:$(WEB_PORT)"; echo "  API:   http://localhost:$(API_PORT)/docs"; echo "  Admin: http://localhost:$(API_PORT)/admin"; echo ""
endef

install: .env ## uv sync, pnpm install, pre-commit install
	uv sync --all-groups
	cd web && pnpm install
	uv run pre-commit install

warm: .env ## Прогрев кэшей (образы, колёса, пакеты) — запускать с интернетом
	docker pull python:3.13-slim
	docker pull node:lts-alpine
	docker pull nginx:alpine
	docker pull postgres:17-alpine
	docker pull redis:7-alpine
	docker pull stoplight/prism:5
	docker pull ghcr.io/astral-sh/uv:0.9.13
	docker build -f docker/Dockerfile.api --target deps --build-arg UV_GROUPS=--all-groups -t hackathon-warm:deps .
	docker rmi hackathon-warm:deps
	$(COMPOSE) build
	uv sync --all-groups
	cd web && pnpm install

up: .env ## Dev-режим (с перезагрузкой кода)
	$(COMPOSE) build
	$(COMPOSE) up -d
	$(urls)

demo: .env ## Demo-сборка: без reload, без dev-зависимостей
	$(COMPOSE_DEMO) build
	$(COMPOSE_DEMO) up -d
	$(urls)

stop: ## Остановить без удаления
	$(COMPOSE) stop

down: ## Удалить контейнеры и сети (тома остаются)
	$(COMPOSE) --profile mock down

restart: ## Перезапуск сервисов
	$(COMPOSE) restart

rm: ## Удалить контейнеры, ТОМА и сети (данные БД теряются)
	@read -r -p "Удалить контейнеры И данные БД? [y/N] " a; \
	  if [ "$$a" = "y" ] || [ "$$a" = "Y" ]; then $(COMPOSE) --profile mock down -v; else echo "Отменено"; fi

logs: ## Логи (make logs s=api)
	$(COMPOSE) logs -f --tail=100 $(s)

ps: ## Состояние сервисов
	$(COMPOSE) ps

shell: ## Оболочка в контейнере api
	$(COMPOSE) exec api bash 2>/dev/null || $(COMPOSE) exec api sh

db-shell: ## psql в контейнере db
	$(COMPOSE) exec db sh -c 'psql -U $$POSTGRES_USER -d $$POSTGRES_DB'

migrate: ## Применить миграции
	$(COMPOSE) run --rm migrate

makemigration: ## Новая миграция: make makemigration m="описание"
	@test -n "$(m)" || (echo 'Укажите m="описание"'; exit 1)
	$(COMPOSE) run --rm migrate alembic revision --autogenerate -m "$(m)"

test: ## pytest в контейнере (LOCAL=1 — локально через uv, нужны db+redis на localhost)
ifdef LOCAL
	uv run pytest
else
	$(COMPOSE) up -d db redis
	$(COMPOSE) run --rm --no-deps api pytest
endif

lint: ## Ruff: проверка
	uv run ruff check . && uv run ruff format --check .

fmt: ## Ruff: форматирование
	uv run ruff check --fix . ; uv run ruff format .

typecheck: ## ty (не блокирует)
	-uv run ty check

contracts: ## Выгрузить OpenAPI в contracts/openapi.json
	uv run python -m scripts.export_openapi

front-gen: ## Сгенерировать типы клиента из контракта
	cd web && pnpm gen-api

mock: ## Prism-мок по контракту (фронт: VITE_API_URL=http://localhost:4010)
	$(COMPOSE) --profile mock up mock

pull: ## Подтянуть образы из GHCR (задайте IMAGE_REGISTRY=ghcr.io/<owner>/<repo>)
	@test -n "$(IMAGE_REGISTRY)" || (echo "Задайте IMAGE_REGISTRY=ghcr.io/<owner>/<repo>"; exit 1)
	docker pull $(IMAGE_REGISTRY)/api:latest
	docker pull $(IMAGE_REGISTRY)/web:latest
	docker tag $(IMAGE_REGISTRY)/api:latest hackathon-api:demo
	docker tag $(IMAGE_REGISTRY)/web:latest hackathon-web:demo

save-images: ## Сохранить demo-образы в images/*.tar для оффлайна
	mkdir -p images
	docker save -o $(IMAGES_TAR) $(IMAGES) postgres:17-alpine redis:7-alpine

load-images: ## Загрузить образы из images/*.tar
	docker load -i $(IMAGES_TAR)
