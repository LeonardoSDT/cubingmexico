#!/usr/bin/env sh
set -e

if [ "$1" = "migrate" ]
then
    python manage.py migrate
    exit 0
fi

if [ "$1" = "makemigrations" ]
then
    python manage.py makemigrations
    exit 0
fi

if [ "$1" = "createsuperuser" ]
then
    python manage.py createsuperuser
    exit 0
fi

if [ "$1" = "runserver_prod" ]
then
    gunicorn -k gevent cubingmexico.wsgi -b 0.0.0.0:8080 --access-logfile - --error-logfile -
    exit 0
fi

if [ "$1" = "syncwca" ]
then
    sh /sync_wca_database.sh
    exit 0
fi

exec "$@"