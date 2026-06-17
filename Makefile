# Makefile для Django-проекта — с цветами, табами и удобным интерфейсом

# Цвета
RED    = \033[0;31m
GREEN  = \033[0;32m
YELLOW = \033[1;33m
BLUE   = \033[0;34m
RESET  = \033[0m

# Константы
UV      = uv run
PYTHON  = python3
DC = docker compose

include .env
export


# Помощь: показать все команды с описанием
.PHONY: help
help:
	@awk -F':.*## ' '/^[a-zA-Z_-]+:.*## / { \
		printf "    \033[36mmake %-12s\033[0m — %s\n", $$1, $$2 \
	} \
	/^[[:space:]]*##==/ { \
		gsub("##==", "", $$0); \
		gsub("[[:space:]]*$$", "", $$0); \
		printf "\033[1;33m🔧 %s\033[0m\n", $$0 \
	}' $(MAKEFILE_LIST)

##==Работа с Docker compose

.PHONY: build
build: ## Собрать и запустить docker контейнеры без отображения логов
	$(DC) up --build -d
	@echo -e "${GREEN}✅ Готово!"

.PHONY: dev
dev: ## Запустить docker контейнеры
	$(DC) up --build
	@echo -e "${GREEN}✅ Готово!"

.PHONY: down
down: ## Удалить контейнеры и volumes
	$(DC) down -v
	@echo -e "${GREEN}✅ Готово!"

##==Взаимодействие с зависимостями:

.PHONY: venv
venv: ## Создать виртуальное окружение (venv)
	@echo -e "${GREEN}Создаём виртуальное окружение...${RESET}"
	uv venv
	@echo -e "${GREEN}✅ Готово: ./venv/${RESET}"

.PHONY: install
install: ## Установить зависимости
	@echo -e "${GREEN}Устанавливаем зависимости...${RESET}"
	${UV} sync
	@echo -e "${GREEN}✅ Завершено${RESET}"

##==Тестирование:

.PHONY: test
test: ## Запустить тесты
	@echo -e "${GREEN}Запускаем тесты...${RESET}"
	$(UV) pytest
	@echo -e "${GREEN}✅ Завершено${RESET}"

.PHONY: lint
lint: ## Запустить линтер
	@echo -e "${GREEN}Запускаем линтер...${RESET}"
	$(UV) ruff check ./booking_service
	@echo -e "${GREEN}✅ Завершено${RESET}"

SHELL := /bin/bash
