.ONESHELL:
.SILENT: test build run-test job run-job run-service call-service clean

ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
SOURCES=$(wildcard $(ROOT_DIR)/input/*.csv)
OBJECTS=$(subst input,output,$(subst .csv,.out,$(SOURCES)))

UID := $(shell id -u)
GID := $(shell id -g)

DOCKER_COMPOSE := UID=${UID} GID=${GID} docker-compose

build:
	[ -f .env ] || cp .env.example .env

	$(DOCKER_COMPOSE) build
	
	$(DOCKER_COMPOSE) run -u root --entrypoint="chown -R ${UID}:${GID} /var/lib/mysql" db
	$(DOCKER_COMPOSE) up -d db
	
	cd job
	[ -f .env ] || ln -s ../.env .env

	cd ../service
	[ -f .env ] || cp ../.env .env

test:
	$(DOCKER_COMPOSE) run --entrypoint="make ${MAKEFLAGS} TARGET=${TARGET} run-test" job

run-test:
ifneq ("$(TARGET)","")
	cd job
	python -m unittest ${TARGET}
else
	python -m unittest discover -s ./job/tests/ -p *_test.py -t ./job/
endif

job: $(OBJECTS)
	@$(MAKE) $(OBJECTS)

run-job:
	$(DOCKER_COMPOSE) run --entrypoint="make ${MAKEFLAGS} job" job

run-service:
	$(DOCKER_COMPOSE) up -d server

restart-service:
	$(DOCKER_COMPOSE) restart service server

call-service:
	echo "Requesting daily driven km for vehicle bern-2, between the dates 2023-03-29 and 2023-03-31."
	echo ""
	curl 'http://localhost:8000/api/driving-distances?vehicle_id=bern-2&start_date=2023-03-29&end_date=2023-03-31'
	echo ""
	echo ""
	echo "Try also on browser with: http://localhost:8000/api/driving-distances?vehicle_id=bern-2&start_date=2023-03-29&end_date=2023-03-31"

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