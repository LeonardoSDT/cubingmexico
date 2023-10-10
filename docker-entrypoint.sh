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
    gunicorn --bind 0.0.0.0:$PORT --reload --workers 1 --threads 8 --timeout 0 cubingmexico.wsgi:application
    exit 0
fi

if [ "$1" = "syncwca" ]
then
    sh /sync_wca_database.sh
    exit 0
fi

if [ "$1" = "statecomps" ]
then
    sh /determine_competition_state.sh
    exit 0
fi

exec "$@"