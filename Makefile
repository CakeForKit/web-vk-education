DC := ./docker-compose.yml
MANGE_PY := ./ask_permyakova/manage.py

.PHONY: run 
run:
	./run.sh

.PHONY: db_run
db_run:
	docker compose -f $(DC) up --build askpermyakova_postgres -d

.PHONY: db_start
db_start:
	docker compose -f $(DC) start askpermyakova_postgres 

.PHONY: db_stop
db_stop:
	docker compose -f $(DC) stop askpermyakova_postgres 

.PHONY: db_down
db_down:
	docker compose -f $(DC) down -v askpermyakova_postgres 

.PHONY: fill_db
fill_db:
	python $(MANGE_PY) fill_db 100

.PHONY: db_clear
db_clear: db_down db_run

.PHONY: remakemigrations
remakemigrations:
	find ./ask_permyakova/app/migrations/ -type f ! -name '__init__.py' -delete
	python3 $(MANGE_PY) makemigrations
	python3 $(MANGE_PY) migrate
	make fill_db

.PHONY: migrate
migrate:
	python3 $(MANGE_PY) migrate

.PHONY: showmigrations
showmigrations:
	python3 $(MANGE_PY) showmigrations

.PHONY: superuser
superuser:
	DJANGO_SUPERUSER_USERNAME=admin \
	DJANGO_SUPERUSER_EMAIL=admin@example.com \
	DJANGO_SUPERUSER_PASSWORD=admin \
	python $(MANGE_PY) createsuperuser --noinput