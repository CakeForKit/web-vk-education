FROM python:3.10-slim-bookworm

# Отключает создание .pyc файлов (байт-код Python)
ENV PYTHONDONTWRITEBYTECODE=1   
# Отключает буферизацию вывода Python
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# RUN apk add --no-cache bash curl gcc

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

WORKDIR /app/ask_permyakova

CMD ["/usr/local/bin/python3", "manage.py", "runserver", "0.0.0.0:8000"]