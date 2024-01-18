# Используем базовый образ с Python
FROM python:3.11

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y libaio1 libaio-dev

# Копируем Oracle Instant Client в контейнер
COPY bot/app/instantclient-basic-linux.x64-21.11.0.0.0dbru.zip /tmp/

# Распаковываем и устанавливаем Oracle Instant Client
RUN unzip /tmp/instantclient-basic-linux.x64-21.11.0.0.0dbru.zip -d /usr/local/
RUN ln -s /usr/local/instantclient_21_11/ /usr/local/instantclient
ENV LD_LIBRARY_PATH /usr/local/instantclient

# Создаем рабочий каталог
WORKDIR /project

# Копируем .env файл внутрь контейнера
COPY . .

# Устанавливаем зависимости из requirements.txt
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN pip install wheel setuptools pip --upgrade

# Установка переменных окружения
ENV TOKEN_API='BOT_TOKEN_API'

ENV ORACLE_USER='ORACLE_USER'
ENV ORACLE_PASSWORD='ORACLE_PASSWORD'
ENV ORACLE_DSN='ORACLE_DSN'

ENV ADMINS=123456789,123456789
ENV SEND_NOTIFICATION='ON'
ENV EMAIL_PASSWORD='EMAIL_PASSWORD'

# Запускаем ваш проект с помощью run.py
CMD ["python", "run.py"]
