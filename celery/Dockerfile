FROM python:3.10

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
WORKDIR /app/ask_permyakova

CMD ["celery", "-A", "ask_permyakova", "worker", "-l", "INFO"]