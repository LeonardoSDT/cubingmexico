FROM python:3

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install -y curl unzip

COPY ./web /code
WORKDIR /code

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
COPY ./sync_wca_database.sh /sync_wca_database.sh
RUN chmod +x /docker-entrypoint.sh
# ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 8080
CMD exec gunicorn --bind 0.0.0.0:$PORT --reload --workers 1 --threads 8 --timeout 0 cubingmexico.wsgi:application
