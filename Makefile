DC := ./docker-compose.yml
MANGE_PY := ./ask_permyakova/manage.py

.PHONY: all
all: db_start nginx_run app_run centrifugo_up

.PHONY: app_run 
app_run:
	docker compose -f $(DC) build askpermyakova_app
	docker compose -f $(DC) up askpermyakova_app -d
# 	./run.sh

.PHONY: app_down
app_down:
	docker compose -f $(DC) down -v askpermyakova_app 

.PHONY: centrifugo_up
centrifugo_up:
	docker compose -f $(DC) up --build askpermyakova_centrifugo -d

.PHONY: centrifugo_down
centrifugo_down:
	docker compose -f $(DC) down -v askpermyakova_centrifugo 

.PHONY: restart_nginx
restart_nginx:
	docker compose -f $(DC) restart askpermyakova_nginx

.PHONY: nginx_run
nginx_run:
	docker compose -v -f $(DC) up --build askpermyakova_nginx -d

.PHONY: nginx_down
nginx_down:
	docker compose -f $(DC) down -v askpermyakova_nginx

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

.PHONY: celery_up
celery_up:
	docker compose -f $(DC) up --build askpermyakova_celery -d

.PHONY: celery_down
celery_down:
	docker compose -f $(DC) down -v askpermyakova_celery 

.PHONY: redis_up
redis_up:
	docker compose -f $(DC) up --build askpermyakova_redis -d

.PHONY: redis_down
redis_down:
	docker compose -f $(DC) down -v askpermyakova_redis 

.PHONY: gunicorn_run
gunicorn_run:
	docker compose -v -f $(DC) up --build gunicorn

.PHONY: gunicorn_down
gunicorn_down:
	docker compose -f $(DC) down -v gunicorn