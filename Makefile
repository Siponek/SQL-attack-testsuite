VENV := venv-sql
ifeq ($(OS),Windows_NT)
	detected_OS := Windows
	PYTHON := $(VENV)/Scripts/python.exe
	PYTEST := $(PYTHON) -m pytest
	PIP := $(VENV)/Scripts/pip
else
	detected_OS := $(shell uname -s)
	PYTHON := $(VENV)/bin/python
	PIP := $(VENV)/bin/pip
endif


.PHONY: reqs
reqs:
	pipreqs --force --encoding=utf8 ./ --ignore ./venv-sql/

.PHONY: clean
clean:
	rm -rf ./$(VENV)/

.PHONY: venv
venv:
	python -m venv $(VENV)

.PHONY: install_reqs
install_reqs: venv
	$(PIP) install -r requirements.txt

.PHONY: test
test:
	$(PYTEST) -v

.PHONY: build
build:
	docker-compose build

.PHONY: up
up:
	docker-compose up

.PHONY: down
down:
	docker-compose down

.PHONY: run-all
run-all: install_reqs build up test down