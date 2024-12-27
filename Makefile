.ONESHELL:
.SILENT: test build run-test job run-job run-service call-service clean

ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
SOURCES=$(wildcard $(ROOT_DIR)/input/*.csv)
OBJECTS=$(subst input,output,$(subst .csv,.out,$(SOURCES)))

DOCKER_COMPOSE := docker compose

build:
	[ -n "$(which ${DOCKER_COMPOSE})" ] || (echo "Docker Compose v2 must be installed to run tests." && exit 1)
	[ -f .env ] || cp .env.example .env
	$(DOCKER_COMPOSE) build

test:
	[ -n "$(which poetry)" ] || (echo "Poetry must be installed to run tests." && exit 1)
	
	cd ${ROOT_DIR}/api
	poetry install
	poetry run pytest .

	cd ${ROOT_DIR}/ddmc
	poetry install
	poetry run pytest .

integration-test:
	[ -n "$(which poetry)" ] || (echo "Poetry must be installed to run tests." && exit 1)
	
	cd ${ROOT_DIR}/api
	poetry install
	poetry run pytest --integration -m integration .

	cd ${ROOT_DIR}/ddmc
	poetry install
	poetry run pytest --integration -m integration .

run-job:
	$(DOCKER_COMPOSE) run job

run-service:
	$(DOCKER_COMPOSE) up -d server

restart-service:
	$(DOCKER_COMPOSE) restart service server

call-service:
	[ -n "$(which curl)" ] || (echo "cURL must be installed to run tests." && exit 1)
	echo "Requesting daily driven km for vehicle bern-2, between the dates 2023-03-29 and 2023-03-31."
	echo ""
	curl 'http://localhost:5000/api/driving-distances?vehicle_id=bern-2&start_date=2023-03-29&end_date=2023-03-31'
	echo ""
	echo ""
	echo "Try also on browser with: http://localhost:5000/api/driving-distances?vehicle_id=bern-2&start_date=2023-03-29&end_date=2023-03-31"

clean:
	rm -rf output/*
	touch output/.keep
	$(DOCKER_COMPOSE) down -v

%.out.csv : ../input/%.csv
	cd $(ROOT_DIR)/job
	python main.py -o "$@" -f "$<"

%.out : ../input/%.csv
	cd $(ROOT_DIR)/job
	python main.py -o "$@" -f "$<" --loader=mysql