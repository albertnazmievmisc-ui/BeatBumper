# BeatBumper Makefile

.PHONY: run test clean setup

# Запуск игры
run:
	python3 main.py

# Запуск тестов
test:
	python3 -m pytest tests/ -v

# Очистка временных файлов
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Установка зависимостей
setup:
	pip3 install -r requirements.txt

# Создание структуры проекта (этот скрипт)
scaffold:
	python3 setup_project.py

# Запуск с отладкой
debug:
	python3 -m pdb main.py

# Проверка стиля кода
lint:
	black --check src/
	mypy src/

# Форматирование кода
format:
	black src/
